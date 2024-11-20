from aiogram.fsm.state import StatesGroup, State


class MenuState(StatesGroup):
    send_msg = State()
    add_group = State()
    group_username = State()



class Send_message(StatesGroup):
    group_chosen = State()
    message = State()
    interval = State()
    confirmation = State()
    get_del_id = State()
