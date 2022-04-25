from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message

from aiogram_dialog import Dialog, DialogManager, Window, StartMode
from aiogram_dialog.manager.protocols import LaunchMode
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from database import ActiveUsers
from bot import MyBot
from user import UserSG, RegistrationSG
from admin import AdminSG


class RootAdminSG(StatesGroup):
    root_admin = State()


async def start(m: Message, dialog_manager: DialogManager):
    if await ActiveUsers.filter(user_id=m.from_user.id).values_list("is_admin"):
        await dialog_manager.start(RootAdminSG.root_admin, mode=StartMode.RESET_STACK)
        # Если админ
    elif not (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id")):
        await dialog_manager.start(RegistrationSG.hi, mode=StartMode.RESET_STACK)
        # Если его нет в базе, то предлагаем зарегистрироваться
        dialog_manager.current_context().dialog_data["id"] = m.from_user.id
    else:
        await MyBot.bot.send_message(m.from_user.id, f'Привет, '
                                                     f'<b>{"".join((await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_name"))[0])}!</b>',
                                     parse_mode="HTML")
        # Если он есть то переходим в меню
        await dialog_manager.start(UserSG.menu, mode=StartMode.RESET_STACK)
        dialog_manager.current_context().dialog_data["name"] = \
            (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_name"))[0]
        dialog_manager.current_context().dialog_data["grade"] = \
            (await ActiveUsers.filter(user_id=m.from_user.id).values_list("grade"))[0]


root_admin_dialog = Dialog(
    Window(
        Const("Выбери действие 🤔"),
        Start(Const("Хочу побыть админом"), id="an", state=AdminSG.admin),
        Start(Const("Хочу побыть юзером"), id="po", state=UserSG.admin_menu),
        state=RootAdminSG.root_admin
    ),
    launch_mode=LaunchMode.ROOT
)

# Регистрируем хэндлер start
MyBot.register_handler(method=start, text="/start", state="*")
MyBot.register_dialogs(root_admin_dialog)
