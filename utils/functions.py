import os

from db.models import Users


def to_dict(message):
    return {
        "message_id": message.message_id,
        "group_id": message.group_id,
        "user_id": message.user_id,
        "job_name": message.job_name,
        "schedule": message.schedule
    }


async def check_user(chat_id):
    user = await Users.get_user_id(id_=str(chat_id))
    return bool(user and user.is_admin)


def get_super_admin_ids() -> set[int]:
    raw = os.getenv("ADMIN", "")
    values = [item.strip() for item in raw.split(",") if item.strip()]
    admin_ids: set[int] = set()
    for value in values:
        if value.isdigit():
            admin_ids.add(int(value))
    return admin_ids


async def is_user_admin(chat_id: int) -> bool:
    if chat_id in get_super_admin_ids():
        return True
    return await check_user(chat_id)