from bot.handlers.admin import admin_router
from bot.handlers.group_add import group_add
from bot.handlers.send_message import message_router
from bot.handlers.start_handler import main_router
from bot.handlers.tasks_info_del import task_info
from utils.dispatcher import dp

dp.include_routers(*[
    main_router,
    group_add,
    message_router,
    task_info,
    admin_router
])
