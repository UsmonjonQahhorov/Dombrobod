from sqlalchemy.util import await_only

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
    data = await Users.get_user_id(id_=str(chat_id))
    return data.__dict__.get("is_admin")