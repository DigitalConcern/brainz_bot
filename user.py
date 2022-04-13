from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back
from aiogram_dialog.widgets.text import Const, Format

from database import ActiveUsers, Questions
from bot import MyBot
from config import Counter, NameCounter, CHAT_ID


# Класс состояний регистрации пользователя
class RegistrationSG(StatesGroup):
    hi = State()
    name = State()
    grade = State()
    choose_grade = State()


# Класс состояний пользователя
class UserSG(StatesGroup):
    menu = State()
    ask = State()
    final = State()


async def get_data(dialog_manager: DialogManager, **kwargs):
    return {
        'id': dialog_manager.current_context().dialog_data.get("id", None),
        'name': dialog_manager.current_context().dialog_data.get("name", None),
        'grade': dialog_manager.current_context().dialog_data.get("grade", None),
    }


async def start(m: Message, dialog_manager: DialogManager):
    if not (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id")):
        await dialog_manager.start(RegistrationSG.hi, mode=StartMode.RESET_STACK)
        # Если его нет в базе, то предлагаем зарегистрироваться
        dialog_manager.current_context().dialog_data["id"] = m.from_user.id
    else:
        await dialog_manager.start(UserSG.menu, mode=StartMode.RESET_STACK)
        # Если он есть то переходим в меню
        dialog_manager.current_context().dialog_data["name"] = \
            (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_name"))[0]
        dialog_manager.current_context().dialog_data["grade"] = \
            (await ActiveUsers.filter(user_id=m.from_user.id).values_list("grade"))[0]

MyBot.register_handler(method=start, text="/start", state="*")


async def name_handler(m: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
    manager.current_context().dialog_data["name"] = m.text
    await manager.dialog().switch_to(RegistrationSG.grade)


# Если студент нажал кнопку "студент"
async def on_student_clicked(c: CallbackQuery, button: Button, manager: DialogManager):
    count = NameCounter.get_count()
    manager.current_context().dialog_data["grade"] = "12"
    while await ActiveUsers.filter(code_name=count).values_list():
        count = NameCounter.get_count()
    await ActiveUsers(user_id=manager.current_context().dialog_data["id"],
                      code_name=count,
                      user_name=manager.current_context().dialog_data["name"],
                      grade="12"
                      ).save()
    await MyBot.bot.send_message(manager.current_context().dialog_data["id"], "Поздравляю, вы зареганы!")
    await manager.done()
    await manager.start(UserSG.menu, mode=StartMode.RESET_STACK)


# Выбор класса обучения (для школьников)
async def on_grade_clicked(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    count = NameCounter.get_count()
    manager.current_context().dialog_data["grade"] = item_id
    while await ActiveUsers.filter(code_name=count).values_list():
        count = NameCounter.get_count()
    await ActiveUsers(user_id=manager.current_context().dialog_data["id"],
                      code_name=count,
                      user_name=manager.current_context().dialog_data["name"],
                      grade=manager.current_context().dialog_data["grade"]
                      ).save()
    await MyBot.bot.send_message(manager.current_context().dialog_data["id"], "Поздравляю, вы зареганы!")
    await manager.done()
    await manager.start(UserSG.menu)

# Диалог регистрации пользователя
registration_dialog = Dialog(
    Window(
        Const("Greetings! Мы - КРОК, пройди пжж регистрацию"),
        SwitchTo(Const("Зарегистрироваться!"), id="fi", state=UserSG.name),
        state=RegistrationSG.hi
    ),
    Window(
        Const("Как тебя зовут?"),
        MessageInput(name_handler),
        Back(Const("⏪ Назад")),
        state=RegistrationSG.name
    ),
    Window(
        Const("Ты школьник или студент?"),
        SwitchTo(Const("Школьник"), id="school", state=UserSG.choose_grade),
        Button(Const("Студент"), id="student", on_click=on_student_clicked),
        Back(Const("⏪ Назад")),
        state=RegistrationSG.grade
    ),
    Window(
        Const("В каком ты классе?"),
        Back(Const("⏪ Назад")),
        Row(Select(
            Format("{item}"),
            items=["<7",
                   "8",
                   "9",
                   "10",
                   "11"
                   ],
            item_id_getter=lambda x: x,
            id="grades",
            on_click=on_grade_clicked,
        )),
        state=RegistrationSG.choose_grade
    )
)


# Если пользователь задал вопрос
async def quest_handler(m: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
    count = Counter.get_count()
    name = (await ActiveUsers.filter(user_id=m.from_user.id).values_list("code_name", flat=True))[0]
    while await Questions.filter(key=count).values_list():
        count = Counter.get_count()  # Присваиваем вопросу идентификатор (цикл на тот случай если бота перезапустят)
    await MyBot.bot.send_message(CHAT_ID, f'<b>{str(count)}</b>' + '\n' + m.text + "\nОт: " + name, parse_mode="HTML")
    await Questions(key=count, user_id_id=m.from_user.id, question=m.text, is_answered=False).save()
    await manager.dialog().switch_to(UserSG.final)

# Диалог юзера (уже зарегистрирован)
user_dialog = Dialog(
    Window(
        Format("<b>{name}</b>, что тебя интересует?"),
        SwitchTo(Const("Задать вопрос ❓"), id="qu", state=UserSG.ask),
        # Сюда кнопки меню
        parse_mode=ParseMode.HTML,
        getter=get_data,
        state=UserSG.menu
    ),
    Window(
        Const("Введите вопрос"),
        MessageInput(quest_handler),
        Back(Const("⏪ Назад")),
        state=UserSG.ask
    ),
    Window(
        Const('Вопрос отправлен!'),
        state=UserSG.final
    )
)

MyBot.register_dialogs(registration_dialog, user_dialog)
