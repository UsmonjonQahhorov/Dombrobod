import asyncio
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from db.models import Groups



async def main_menu():
    design = [
        [
            KeyboardButton(text="Gurux qo'shish"), KeyboardButton(text="Habar yuborish"),
        ],
        [KeyboardButton(text="Habarlarim"),]
    ]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)


async def groups_button():
    design = []
    data = await Groups.get_all()
    for group_instance in data:
        group_id = group_instance.group_id
        username = group_instance.username
        if group_id and username:
            design.append([KeyboardButton(text=str(username))])
    design.append([KeyboardButton(text="ORTGA CHIQISH")])
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)


async def back_button():
    design = [
        [KeyboardButton(text="ORTGA CHIQISH")],
    ]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)


async def yess_no():
    design = [
        [KeyboardButton(text="HAA")],
        [KeyboardButton(text="YOQ")],
    ]
    return ReplyKeyboardMarkup(keyboard=design, resize_keyboard=True)


