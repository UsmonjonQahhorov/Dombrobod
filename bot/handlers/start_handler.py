from aiogram import html, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.buttons.reply_markup import main_menu
from bot.states import MenuState
from db.models import Users
from utils.functions import get_super_admin_ids, is_user_admin

main_router = Router(name=__name__)

@main_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    from utils.dispatcher import bot

    username = message.from_user.username
    user_id = message.from_user.id
    user = await Users.get_user_id(id_=str(message.from_user.id))
    try:
        if not user:
            await Users.create(username=username, user_id=str(user_id), phone_number="987654321")
        if user_id in get_super_admin_ids():
            await Users.update(id_=str(user_id), is_admin=True)
        await state.set_state(MenuState.add_group)
    except Exception as e:
        await bot.send_message(chat_id=6108693014, text=str(e))

    if await is_user_admin(user_id):
        await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! Menulardan birini tanlang",
                             reply_markup=await main_menu())
    else:
        await message.answer("Siz botdan foydalana olmaysiz. Murojat uchun @U_Qohhorov",
                             reply_markup=ReplyKeyboardRemove())
