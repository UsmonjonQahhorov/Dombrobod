from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from db.models import Users
from utils.functions import is_user_admin

admin_router = Router(name=__name__)


@admin_router.message(Command("admin"))
async def admin_handler(message: Message) -> None:
    if not await is_user_admin(message.from_user.id):
        await message.answer("Sizda ushbu buyruq uchun ruxsat yo'q.")
        return

    target_user_id: str | None = None
    text = message.text or ""
    parts = text.split(maxsplit=1)
    if len(parts) == 2 and parts[1].strip().isdigit():
        target_user_id = parts[1].strip()
    elif message.reply_to_message and message.reply_to_message.from_user:
        target_user_id = str(message.reply_to_message.from_user.id)

    if not target_user_id:
        await message.answer("Format: /admin TELEGRAM_USER_ID yoki foydalanuvchi xabariga reply qilib /admin yuboring.")
        return

    target_user = await Users.get_user_id(target_user_id)
    if not target_user:
        await message.answer("Foydalanuvchi topilmadi. Avval u /start bossin.")
        return

    await Users.update(id_=target_user_id, is_admin=True)
    await message.answer(f"{target_user_id} admin qilindi.")
