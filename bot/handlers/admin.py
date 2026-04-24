from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from db.models import Users
from utils.functions import get_super_admin_ids

admin_router = Router(name=__name__)


@admin_router.message(Command("admin"))
async def admin_handler(message: Message) -> None:
    if message.from_user.id not in get_super_admin_ids():
        await message.answer("Sizda ushbu buyruq uchun ruxsat yo'q.")
        return

    parts = message.text.split(maxsplit=1)
    if len(parts) != 2 or not parts[1].isdigit():
        await message.answer("Format: /admin <telegram_user_id>")
        return

    target_user_id = parts[1]
    target_user = await Users.get_user_id(target_user_id)
    if not target_user:
        await message.answer("Foydalanuvchi topilmadi. Avval u /start bossin.")
        return

    await Users.update(id_=target_user_id, is_admin=True)
    await message.answer(f"{target_user_id} admin qilindi.")
