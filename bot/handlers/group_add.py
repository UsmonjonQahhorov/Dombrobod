from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
from bot.states import MenuState
from db.models import Groups
from bot.buttons.reply_markup import main_menu
from utils.dispatcher import bot

group_add = Router(name=__name__)


@group_add.message(F.text.__eq__("Gurux qo'shish"))
async def group_addition(message: Message, state: FSMContext):
    await message.answer("Gruppaning USERNAME ini jo'nating!", reply_markup=ReplyKeyboardRemove())
    await state.set_state(MenuState.group_username)


@group_add.message(MenuState.group_username)
async def group_username_handler(message: Message, state: FSMContext) -> None:
    group_link = message.text
    try:
        chat_info = await bot.get_chat(group_link)
        chat_title = chat_info.title
        chat_id = chat_info.id
        # group = await Groups.get_group_id(id_=str(chat_id))
        group = []
        if group == []:
            print("hato")
            await Groups.create(group_id=str(chat_id), username=str(chat_title))
            await message.answer("Gurux qoshildi, botdan foydalanishingiz mumkin!", reply_markup=await main_menu())
        else:
            await message.answer("Bu gurux allaqachon qoshilgan.", reply_markup=await main_menu())

        await state.set_state("main_menu")

    except Exception as e:
        await message.answer(f"Xatolik yuz berdi: {str(e)}. Iltimos, guruh username ni to'g'ri formatda yuboring.")
        await state.set_state("main_menu")
