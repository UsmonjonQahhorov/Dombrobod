from aiogram import html, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from db.models import Users
from bot.buttons.reply_markup import main_menu, groups_button
from bot.states import MenuState
from utils.functions import check_user

main_router = Router(name=__name__)


@main_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    from utils.dispatcher import bot
    await bot.delete_webhook(drop_pending_updates=True)

    status = await check_user(chat_id=message.from_user.id)
    if status:
        await message.answer(f"Hello, {html.bold(message.from_user.full_name)}! Menulardan birini tanlang",
                             reply_markup=await main_menu())
        username = message.from_user.username
        user_id = message.from_user.id
        user = await Users.get_user_id(id_=str(message.from_user.id))
        # print(user)
        try:
            if not user:
                await Users.create(username=username, user_id=str(user_id), phone_number="987654321")
            await state.set_state(MenuState.add_group)
        except Exception as e:
            await bot.send_message(chat_id=6108693014, text=e)
    else:
        await message.answer("Siz botdan foydalana olmaysiz. Murojat uchun @U_Qohhorov")
