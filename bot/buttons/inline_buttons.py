from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters.callback_data import CallbackData



class MyCallback(CallbackData, prefix="delete"):
    name: str
    task_id: str


async def delete(task_id):
    design = [
        [InlineKeyboardButton(text="O'chirish", callback_data=MyCallback(name="delete_task", task_id=task_id).pack())]
    ]

    return InlineKeyboardMarkup(inline_keyboard=design)
