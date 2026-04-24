from datetime import datetime, timedelta
from uuid import uuid4

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db.models import Groups, Messages, Users


ADMIN_CHAT_ID = 6108693014
scheduler = AsyncIOScheduler()
task_registry: dict[str, dict] = {}


def ensure_scheduler_started() -> None:
    if not scheduler.running:
        scheduler.start()


async def create_task_func(job_id: str, chat_id: str, message_id: int, from_chat_id: int) -> None:
    from utils.dispatcher import bot

    try:
        await bot.forward_message(chat_id=chat_id, message_id=message_id, from_chat_id=from_chat_id)
    except Exception as exc:
        error_text = str(exc)
        # Auto-clean invalid jobs to avoid endless failing retries.
        if "message to forward not found" in error_text.lower():
            remove_task(job_id)
            await Messages.delete_task(job_id)
        await bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"Forwarding failed ({job_id}): {error_text}")


async def schedule_forwarding(
    group_id: str,
    message_id: int,
    from_chat_id: int,
    days_: int,
    hours_: int,
    minutes_: int,
) -> str:
    ensure_scheduler_started()
    job_id = str(uuid4())
    interval_kwargs = {"hours": hours_, "minutes": minutes_}
    if hours_ == 0 and minutes_ == 0:
        interval_kwargs = {"days": 1}

    job = scheduler.add_job(
        create_task_func,
        "interval",
        **interval_kwargs,
        args=(job_id, group_id, message_id, from_chat_id),
        end_date=datetime.now() + timedelta(days=days_),
        id=job_id,
        replace_existing=False,
    )
    task_registry[job_id] = {
        "group_id": group_id,
        "message_id": message_id,
        "from_chat_id": from_chat_id,
        "days": days_,
        "hours": hours_,
        "minutes": minutes_,
        "job": job,
    }

    group = await Groups.get_group_id(group_id)
    user = await Users.get_user_id(str(from_chat_id))
    if not group or not user:
        raise ValueError("User or group not found for scheduling")

    await Messages.create(
        message_id=message_id,
        group_id=int(group.id),
        user_id=int(user.id),
        job_name=job_id,
        schedule=f"{days_}-{hours_}-{minutes_}",
    )
    return job_id


def remove_task(job_id: str) -> bool:
    job = scheduler.get_job(job_id)
    if job:
        job.remove()
    elif job_id not in task_registry:
        return False

    if job_id in task_registry:
        del task_registry[job_id]
    return True


def _parse_schedule(schedule: str) -> tuple[int, int, int]:
    days_str, hours_str, minutes_str = schedule.split("-")
    return int(days_str), int(hours_str), int(minutes_str)


async def restore_jobs_from_db() -> None:
    ensure_scheduler_started()
    tasks = await Messages.get_all()
    for task in tasks:
        if not task.job_name:
            continue
        if scheduler.get_job(task.job_name):
            continue

        group = await Groups.get(task.group_id)
        user = await Users.get(task.user_id)
        if not group or not user:
            continue

        try:
            days_, hours_, minutes_ = _parse_schedule(task.schedule)
        except (ValueError, AttributeError):
            continue
        if days_ == 0 and hours_ == 0 and minutes_ == 0:
            continue
        interval_kwargs = {"hours": hours_, "minutes": minutes_}
        if hours_ == 0 and minutes_ == 0:
            interval_kwargs = {"days": 1}

        end_date = datetime.now() + timedelta(days=max(days_, 1))
        job = scheduler.add_job(
            create_task_func,
            "interval",
            **interval_kwargs,
            args=(task.job_name, group.group_id, task.message_id, int(user.user_id)),
            end_date=end_date,
            id=task.job_name,
            replace_existing=False,
        )
        task_registry[task.job_name] = {
            "group_id": group.group_id,
            "message_id": task.message_id,
            "from_chat_id": int(user.user_id),
            "days": days_,
            "hours": hours_,
            "minutes": minutes_,
            "job": job,
        }