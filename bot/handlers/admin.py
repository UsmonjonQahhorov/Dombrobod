from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from sqlalchemy.util import await_fallback

from bot.buttons.inline_buttons import delete
from bot.buttons.reply_markup import groups_button, main_menu, back_button, yess_no
from bot.states import Send_message
from db.models import Groups, Messages, Users
from utils.dispatcher import bot
from utils.functions import to_dict
from utils.scheduler import schedule_forwarding, remove_task

admin_router = Router(name=__name__)


@admin_router.message(Command("admin"))
async def admin_handler(message: Message, state: FSMContext) -> None:
    if message.from_user.id == 6108693014:
        await Users.update(id_=message.text, is_admin=True)
        await message.answer("User adminga aylandi")

