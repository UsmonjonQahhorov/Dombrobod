from aiogram import F, Router
from aiogram.types import Message

from bot.buttons.inline_buttons import delete
from db.models import Messages, Users
from utils.dispatcher import bot
from utils.functions import to_dict
from utils.telegram_safe import safe_answer, with_telegram_retry

task_info = Router(name=__name__)

@task_info.message(F.text.__eq__("Habarlarim"))
async def task_information(msg: Message):
    user = await Users.get_user_id(str(msg.from_user.id))
    if not user:
        await safe_answer(msg, "Foydalanuvchi topilmadi.")
        return

    tasks = await Messages.get_all()
    own_tasks = [task for task in tasks if task.user_id == user.id]
    if own_tasks:
        messages_dict_list = [to_dict(item) for item in own_tasks]
        for msg_dict in messages_dict_list:
            try:
                delete_markup = await delete(task_id=msg_dict.get("job_name"))
                await with_telegram_retry(
                    lambda: bot.forward_message(
                        chat_id=msg.from_user.id,
                        from_chat_id=msg.from_user.id,
                        message_id=msg_dict.get("message_id"),
                    )
                )
                await with_telegram_retry(
                    lambda: bot.send_message(
                        chat_id=msg.from_user.id,
                        text="USHBU HABARNI O'CHIRISH UCHUN O'CHIRISH TUGMASINI BOSING",
                        reply_markup=delete_markup,
                    )
                )
            except Exception:
                await safe_answer(msg, "Habarlar ro'yxatini yuborishda tarmoq xatosi. Qayta urinib ko'ring.")
                return
    else:
        await safe_answer(msg, "SIZDA HABARLAR YOQ")



