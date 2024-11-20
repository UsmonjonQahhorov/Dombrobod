from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from sqlalchemy.util import await_fallback

from bot.buttons.inline_buttons import delete
from bot.buttons.reply_markup import groups_button, main_menu, back_button, yess_no
from bot.states import Send_message
from db.models import Groups, Messages
from utils.dispatcher import bot
from utils.functions import to_dict
from utils.scheduler import schedule_forwarding, remove_task

task_info = Router(name=__name__)

@task_info.message(F.text.__eq__("Habarlarim"))
async def task_information(msg: Message):
    tasks = await Messages.get_all()
    if tasks:
        messages_dict_list = [to_dict(msg) for msg in tasks]
        for msg_dict in messages_dict_list:
            await bot.forward_message(
                chat_id=6108693014,
                from_chat_id=msg.from_user.id,
                message_id=msg_dict.get('message_id')
            )

            await bot.send_message(
                chat_id=6108693014,
                text=f"USHBU HABARNI OCHIRISH UCHUN O'CHIRISH TUGMASINI BOSING",
                reply_markup=await delete(task_id=msg_dict.get('job_name'))
            )
    else:
        await msg.answer("SIZDA HABARLAR YOQ")



