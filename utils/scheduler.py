from datetime import datetime, timedelta
from uuid import uuid4
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from db.models import Messages, Groups, Users
from utils.dispatcher import bot


scheduler = AsyncIOScheduler()
task_registry = {}
# scheduler = BackgroundScheduler()


async def create_task_func(chat_id, message_id, from_chat_id):
    try:
        await bot.forward_message(chat_id=chat_id, message_id=message_id, from_chat_id=from_chat_id)
    except Exception as e:
        await bot.send_message(chat_id=6108693014, text=e)


async def schedule_forwarding(group_id:int, message_id:int, from_chat_id:int, days_:str, hours_:str, minutes_:str):
    job_id = str(uuid4())
    job = scheduler.add_job(
        create_task_func, 'interval', hours=int(hours_), minutes=int(minutes_),
        args=(group_id, message_id, from_chat_id),
        end_date=datetime.now() + timedelta(days=int(days_)),
        id=job_id
    )
    task_registry[job_id] = {
        "group_id": group_id,
        "message_id": message_id,
        "from_chat_id": from_chat_id,
        "days": days_,
        "hours": hours_,
        "minutes": minutes_,
        "job": job
    }

    group = await Groups.get_group_id(group_id)
    user = await Users.get_user_id(str(from_chat_id))


    await Messages.create(
        message_id=message_id,
        group_id=int(group.id),
        user_id=int(user.__dict__.get('id')),
        job_name=job_id,
        schedule=f"{str(days_)}-{str(hours_)}-{str(minutes_)}"
    )

    if not scheduler.running:
        scheduler.start()

    return job_id


def remove_task(job_id):
    job_info = task_registry.get(job_id)
    if job_info:
        job_info["job"].remove()
        del task_registry[job_id]
        print(f"Task with ID {job_id} has been deleted.")
    else:
        print(f"No task found with ID {job_id}")