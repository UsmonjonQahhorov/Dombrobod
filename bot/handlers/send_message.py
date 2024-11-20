from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from sqlalchemy.util import await_fallback

from bot.buttons.inline_buttons import MyCallback
from bot.buttons.reply_markup import groups_button, main_menu, back_button, yess_no
from bot.states import Send_message
from db.models import Groups, Messages
from utils.dispatcher import bot
from utils.scheduler import schedule_forwarding, remove_task

from aiogram.types.reply_keyboard_remove import ReplyKeyboardRemove

message_router = Router(name=__name__)


@message_router.message(F.text == "Habar yuborish")
async def echo_handler(message: Message, state: FSMContext) -> None:
    await message.answer(f"HABAR YUBORMOQCHI BOLGAN GURUXNI TANLANG!", reply_markup=await groups_button())
    await state.set_state(Send_message.group_chosen)


@message_router.message(F.text.__eq__("ORTGA CHIQISH"))
async def back_handler(message: Message) -> None:
    await message.answer("SIZ BOSH MENUGA QAYDINGIZ", reply_markup=await main_menu())


@message_router.message(Send_message.group_chosen)
async def message_handler(message: Message, state: FSMContext) -> None:
    group = await Groups.get_group_username(message.text)
    chat_id = group.group_id
    await state.update_data({"chat_id": chat_id})
    await message.answer("YUBORMOQCHI BOLGAN HABARINGIZNI KIRITING", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Send_message.message)


@message_router.message(Send_message.message)
async def messag_save_handler(message: Message, state: FSMContext) -> None:
    await state.update_data({"message_id": message.message_id})
    await message.answer(
        "YUBORISH INTERVALINI KIRITING ([KUN-SOAT-MINUT = 30-1-30])\nAGAR SOAT YOKI MINUT "
        "KIRITISHNI HOHLAMASANGIZ 0 (NOL) KIRITIB KETING",
        reply_markup=await back_button()
    )
    await state.set_state(Send_message.interval)


@message_router.message(Send_message.interval)
async def interval_handler(msg: Message, state: FSMContext) -> None:
    try:
        a, b, c = map(int, msg.text.split("-"))
        await state.update_data({"a": a, "b": b, "c": c})
    except ValueError:
        await msg.answer('INTERVALNI NOTO\'G\'RI KIRITDINGIZ', reply_markup=await back_button())
        return

    data = await state.get_data()
    group_id = data["chat_id"]
    message_id = data["message_id"]

    try:
        group = await Groups.get_group_id(group_id)

        await msg.answer(
            f"FOYDALANUVCHI HABARINGIZNI TEKSHIRING. SIZ YUBORMOQCHI BOLGAN HABAR QUYIDAGI👇👇 VA SIZ UNI"
            f" <b>{group.username}</b> GURUXIGA👉  {a} KUN DAVOMIDA  {b} SOAT VA {c} MINUT INTERVALDA JONATMOQCHIMISIZ?",
            parse_mode=ParseMode.HTML, reply_markup=await yess_no()
        )
        await bot.forward_message(chat_id=msg.from_user.id, message_id=message_id, from_chat_id=msg.from_user.id)
        await state.set_state(Send_message.confirmation)

    except Exception as e:
        await bot.send_message(chat_id=6108693014, text=f"Error: {str(e)}")  # Better error formatting


@message_router.message(Send_message.confirmation)
async def confirmation_handler(msg: Message, state: FSMContext) -> None:
    data = await state.get_data()
    group_id = data["chat_id"]
    message_id = data["message_id"]
    a = int(data["a"])
    b = int(data["b"])
    c = int(data["c"])

    if msg.text == "HAA":
        job_id = await schedule_forwarding(
            group_id=group_id,
            message_id=message_id,
            from_chat_id=msg.from_user.id,
            days_=str(a), hours_=str(b), minutes_=str(c)
        )
        print(job_id)
        await msg.answer('Habar jo\'natish boshlandi', reply_markup=await main_menu())
        await state.clear()

    elif msg.text == "YOQ":
        await msg.answer("BOSH MENUGA QAYDINGIZ", reply_markup=await main_menu())
        await state.clear()
    else:
        await msg.answer("Iltimos, 'HAA' yoki 'YOQ' tugmalarini bosing.", reply_markup=await yess_no())


# Ochirish
# @message_router.message(F.text.__eq__("Delete"))
# async def delete_task_handler(msg: Message, state: FSMContext):
#     await msg.answer("O'CHIRMOQCHI BOLGAN HABARINGIZ ID SINI KIRITING!")
#     await state.set_state(Send_message.get_del_id)


@message_router.callback_query(MyCallback.filter(F.name == "delete_task"))
async def delete_task_handler(query: CallbackQuery, callback_data: MyCallback):
    print(callback_data)
    job_id = str(callback_data.task_id)

    if job_id:
        remove_task(job_id)
        await Messages.delete_task(job_id)
        await query.message.answer("Habaringiz o'chirildi", reply_markup=await main_menu())

    else:
        await query.answer("Hech qanday habar mavjud emas", reply_markup=await main_menu())
