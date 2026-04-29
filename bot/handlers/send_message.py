from aiogram import F, Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from bot.buttons.inline_buttons import MyCallback
from bot.buttons.reply_markup import groups_button, main_menu, back_button, yess_no
from bot.states import Send_message
from db.models import Groups, Messages
from utils.dispatcher import bot
from utils.scheduler import schedule_forwarding, remove_task
from utils.telegram_safe import safe_answer, with_telegram_retry

message_router = Router(name=__name__)


@message_router.message(F.text == "Habar yuborish")
async def echo_handler(message: Message, state: FSMContext) -> None:
    await safe_answer(message, "HABAR YUBORMOQCHI BOLGAN GURUXNI TANLANG!", reply_markup=await groups_button())
    await state.set_state(Send_message.group_chosen)


@message_router.message(F.text.__eq__("ORTGA CHIQISH"))
async def back_handler(message: Message, state: FSMContext) -> None:
    await state.clear()
    await safe_answer(message, "SIZ BOSH MENUGA QAYDINGIZ", reply_markup=await main_menu())

@message_router.message(Send_message.group_chosen)
async def message_handler(message: Message, state: FSMContext) -> None:
    group = await Groups.get_group_username(message.text)
    if not group:
        await safe_answer(message, "Bunday guruh topilmadi. Qaytadan tanlang.", reply_markup=await groups_button())
        return

    chat_id = group.group_id
    await state.update_data({"chat_id": chat_id})
    await safe_answer(message, "YUBORMOQCHI BOLGAN HABARINGIZNI KIRITING", reply_markup=ReplyKeyboardRemove())
    await state.set_state(Send_message.message)


@message_router.message(Send_message.message)
async def messag_save_handler(message: Message, state: FSMContext) -> None:
    await state.update_data({"message_id": message.message_id})
    await safe_answer(
        message,
        "YUBORISH INTERVALINI KIRITING ([KUN-SOAT-MINUT = 30-1-30])\nAGAR SOAT YOKI MINUT "
        "KIRITISHNI HOHLAMASANGIZ 0 (NOL) KIRITIB KETING",
        reply_markup=await back_button()
    )
    await state.set_state(Send_message.interval)


@message_router.message(Send_message.interval)
async def interval_handler(msg: Message, state: FSMContext) -> None:
    try:
        a, b, c = map(int, msg.text.split("-"))
        if a < 0 or b < 0 or c < 0:
            raise ValueError
        if a == 0 and b == 0 and c == 0:
            await safe_answer(msg, "Interval 0 bo'lishi mumkin emas.", reply_markup=await back_button())
            return
        # Stop 1-minute/minute-spam schedules.
        # The actual trigger interval is controlled by hours/minutes (days_ is end_date duration).
        trigger_minutes = b * 60 + c
        if trigger_minutes != 0 and trigger_minutes < 5:
            await safe_answer(
                msg,
                "Interval juda qisqa. Kamida 5 minutdan (yoki 0) foydalaning.",
                reply_markup=await back_button(),
            )
            return
        await state.update_data({"a": a, "b": b, "c": c})
    except ValueError:
        await safe_answer(msg, 'INTERVALNI NOTO\'G\'RI KIRITDINGIZ', reply_markup=await back_button())
        return

    data = await state.get_data()
    group_id = data["chat_id"]
    message_id = data["message_id"]

    try:
        group = await Groups.get_group_id(group_id)

        await safe_answer(
            msg,
            f"FOYDALANUVCHI HABARINGIZNI TEKSHIRING. SIZ YUBORMOQCHI BOLGAN HABAR QUYIDAGI👇👇 VA SIZ UNI"
            f" <b>{group.username}</b> GURUXIGA👉  {a} KUN DAVOMIDA  {b} SOAT VA {c} MINUT INTERVALDA JONATMOQCHIMISIZ?",
            parse_mode=ParseMode.HTML, reply_markup=await yess_no()
        )
        await with_telegram_retry(
            lambda: bot.forward_message(
                chat_id=msg.from_user.id,
                message_id=message_id,
                from_chat_id=msg.from_user.id,
            )
        )
        await state.set_state(Send_message.confirmation)

    except Exception as e:
        await with_telegram_retry(lambda: bot.send_message(chat_id=6108693014, text=f"Error: {str(e)}"))


@message_router.message(Send_message.confirmation)
async def confirmation_handler(msg: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if data.get("confirmation_in_progress"):
        await safe_answer(msg, "So'rov qayta ishlanmoqda, biroz kuting.")
        return
    await state.update_data({"confirmation_in_progress": True})

    if not all(key in data for key in ("chat_id", "message_id", "a", "b", "c")):
        await safe_answer(msg, "So'rov holati eskirgan. Iltimos, qaytadan boshlang.", reply_markup=await main_menu())
        await state.clear()
        return

    group_id = data["chat_id"]
    message_id = data["message_id"]
    a = int(data["a"])
    b = int(data["b"])
    c = int(data["c"])

    if msg.text == "HAA":
        try:
            # Immediate delivery check: fail fast if bot can't forward to the selected group.
            await with_telegram_retry(
                lambda: bot.forward_message(chat_id=group_id, message_id=message_id, from_chat_id=msg.from_user.id)
            )
        except Exception as e:
            await safe_answer(
                msg,
                f"Habarni guruhga yuborib bo'lmadi: {str(e)}\n"
                f"Bot guruhda borligini va yozish huquqi borligini tekshiring.",
                reply_markup=await main_menu(),
            )
            await state.clear()
            return

        try:
            job_id = await schedule_forwarding(
                group_id=group_id,
                message_id=message_id,
                from_chat_id=msg.from_user.id,
                days_=a,
                hours_=b,
                minutes_=c
            )
        except Exception as e:
            await safe_answer(msg, f"Schedule yaratilmadi: {str(e)}", reply_markup=await main_menu())
            await state.clear()
            return

        await safe_answer(msg, f"Habar jo'natish boshlandi. Task ID: {job_id}", reply_markup=await main_menu())
        await state.clear()

    elif msg.text == "YOQ":
        await safe_answer(msg, "BOSH MENUGA QAYDINGIZ", reply_markup=await main_menu())
        await state.clear()
    else:
        await safe_answer(msg, "Iltimos, 'HAA' yoki 'YOQ' tugmalarini bosing.", reply_markup=await yess_no())
        await state.update_data({"confirmation_in_progress": False})


# Ochirish
# @message_router.message(F.text.__eq__("Delete"))
# async def delete_task_handler(msg: Message, state: FSMContext):
#     await msg.answer("O'CHIRMOQCHI BOLGAN HABARINGIZ ID SINI KIRITING!")
#     await state.set_state(Send_message.get_del_id)


@message_router.callback_query(MyCallback.filter(F.name == "delete_task"))
async def delete_task_handler(query: CallbackQuery, callback_data: MyCallback):
    job_id = str(callback_data.task_id)

    if job_id:
        deleted = remove_task(job_id)
        if deleted:
            await Messages.delete_task(job_id)
            await safe_answer(query.message, "Habaringiz o'chirildi", reply_markup=await main_menu())
        else:
            await safe_answer(query.message, "Task topilmadi yoki allaqachon o'chirilgan.", reply_markup=await main_menu())
        try:
            await with_telegram_retry(lambda: query.answer())
        except TelegramBadRequest:
            pass

    else:
        try:
            await with_telegram_retry(lambda: query.answer("Hech qanday habar mavjud emas"))
        except TelegramBadRequest:
            pass
