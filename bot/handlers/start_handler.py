import asyncio
import time

from aiogram import html, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

from bot.buttons.reply_markup import main_menu
from bot.states import MenuState
from db.models import Users
from db import db
from sqlalchemy.exc import IntegrityError

from utils.functions import get_super_admin_ids, is_user_admin
from utils.telegram_safe import safe_answer, with_telegram_retry

main_router = Router(name=__name__)

START_BG_DEBOUNCE_SECONDS = 1.5
_last_start_bg_by_user: dict[int, float] = {}

@main_router.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext) -> None:
    from utils.dispatcher import bot

    user_id = message.from_user.id
    super_admins = get_super_admin_ids()
    is_super_admin = user_id in super_admins

    now = time.monotonic()
    if _last_start_bg_by_user.get(user_id, 0.0) > now - START_BG_DEBOUNCE_SECONDS:
        return
    _last_start_bg_by_user[user_id] = now

    # 1) Instant response: absolutely no DB work here.
    if is_super_admin:
        await state.set_state(MenuState.add_group)
        await safe_answer(
            message,
            f"Hello, {html.bold(message.from_user.full_name)}! Menulardan birini tanlang",
            reply_markup=await main_menu(),
        )
    else:
        # We answer immediately, then verify authorization in background.
        await safe_answer(
            message,
            "Tekshirilmoqda... biroz kuting",
            reply_markup=ReplyKeyboardRemove(),
        )

    # 2) Background DB upsert + authorization check.

    async def bg_start() -> None:
        try:
            username = message.from_user.username
            user = await Users.get_user_id(id_=str(user_id))

            if not user:
                try:
                    await Users.create(
                        username=username,
                        user_id=str(user_id),
                        phone_number="987654321",
                    )
                except IntegrityError:
                    # /start spam can cause duplicate inserts; treat it as success.
                    await db.rollback()

            # Mark super admin in DB (idempotent-ish).
            if is_super_admin:
                await Users.update(id_=str(user_id), is_admin=True)
                return

            if await is_user_admin(user_id):
                await state.set_state(MenuState.add_group)
                await safe_answer(
                    message,
                    f"Hello, {html.bold(message.from_user.full_name)}! Menulardan birini tanlang",
                    reply_markup=await main_menu(),
                )
            else:
                await state.clear()
                await safe_answer(
                    message,
                    "Siz botdan foydalana olmaysiz. Murojat uchun @U_Qohhorov",
                    reply_markup=ReplyKeyboardRemove(),
                )
        except Exception as e:
            await with_telegram_retry(
                lambda: bot.send_message(chat_id=6108693014, text=f"Start handler bg error: {e}"),
                retries=1,
                operation_timeout=2.5,
            )

    asyncio.create_task(bg_start())
