from aiogram import F, Router
from aiogram.types import Message

from bot.buttons.inline_buttons import delete
from db.models import Messages, Users
from utils.dispatcher import bot
from utils.functions import to_dict

task_info = Router(name=__name__)

@task_info.message(F.text.__eq__("Habarlarim"))
async def task_information(msg: Message):
    user = await Users.get_user_id(str(msg.from_user.id))
    if not user:
        await msg.answer("Foydalanuvchi topilmadi.")
        return

    tasks = await Messages.get_all()
    own_tasks = [task for task in tasks if task.user_id == user.id]
    if own_tasks:
        messages_dict_list = [to_dict(item) for item in own_tasks]
        for msg_dict in messages_dict_list:
            await bot.forward_message(
                chat_id=msg.from_user.id,
                from_chat_id=msg.from_user.id,
                message_id=msg_dict.get("message_id"),
            )
            await bot.send_message(
                chat_id=msg.from_user.id,
                text="USHBU HABARNI O'CHIRISH UCHUN O'CHIRISH TUGMASINI BOSING",
                reply_markup=await delete(task_id=msg_dict.get("job_name")),
            )
    else:
        await msg.answer("SIZDA HABARLAR YOQ")



