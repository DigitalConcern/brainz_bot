from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, Back, Column, Start, Cancel
from aiogram_dialog.widgets.text import Const, Format

from database import ActiveUsers, Questions
from bot import MyBot
from config import CHAT_ID

# В данном файле находится интерфейс админа

# Словарь категорий для обработки данных из таблицы активных пользователей
categories = {
    "Всем": ["<7", "8", "9", "10", "11", "12"],
    "Студенты": "12",
    "Школьники": ["<7", "8", "9", "10", "11"]
}


# Класс состояний корневого диалога администратора
class AdminSG(StatesGroup):
    admin = State()


# Класс состояний ветки диалога с ответами на вопросы
class AnswerSG(StatesGroup):
    answer = State()
    ticket = State()
    check = State()


# Класс состояний ветки диалога с постом
class PostSG(StatesGroup):
    post = State()
    to_who = State()
    check = State()


# функция для получения данных из состояний
async def get_data(dialog_manager: DialogManager, **kwargs):
    return {
        'post': dialog_manager.current_context().dialog_data.get("post", None),
        'answer': dialog_manager.current_context().dialog_data.get("answer", None),
        'ticket': dialog_manager.current_context().dialog_data.get("ticket", None),
        'check': dialog_manager.current_context().dialog_data.get("check", None),
        'category': dialog_manager.current_context().dialog_data.get("category", None),
    }


# Хендлер на команду /admin
async def admin(m: Message, dialog_manager: DialogManager):
    await dialog_manager.start(AdminSG.admin, mode=StartMode.RESET_STACK)


MyBot.register_handler(method=admin, text="/admin", state="*")


# Корневой диалог админа
root_admin_dialog = Dialog(
    Window(
        Const("Hello, admin"),
        Start(Const("I want to answer"), id="an", state=AnswerSG.answer),
        Start(Const("I want to post"), id="po", state=PostSG.post),
        state=AdminSG.admin
    ),
    launch_mode=LaunchMode.ROOT
)


async def post_handler(m: Message, dialog: Dialog, manager: DialogManager):
    manager.current_context().dialog_data["post"] = m.text
    await manager.dialog().switch_to(PostSG.to_who)


# Выбор категории
async def on_who_clicked(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    manager.current_context().dialog_data["category"] = item_id
    await manager.dialog().switch_to(PostSG.check)


# Обрабатываем сообщение о подтверждении записи (поста)
async def on_post_ok_clicked(c: CallbackQuery, button: Button, manager: DialogManager):
    for grade in categories[manager.current_context().dialog_data["category"]]:
        await MyBot.bot.send_message(await ActiveUsers.filter(grade=grade).values_list("user_id", flat=True),
                                     manager.current_context().dialog_data["post"])
    await MyBot.bot.send_message(CHAT_ID, "Пост отправлен")
    await manager.done()
    await manager.bg().done()


# Ветка с постом
post_dialog = Dialog(
    Window(
        Const("Please, send post"),
        MessageInput(post_handler),
        Cancel(Const("⏪ Назад")),
        state=PostSG.post
    ),
    Window(
        Const("Кому отправить?"),
        Row(Select(
            Format("{item}"),
            items=["Школьникам",
                   "Студентам",
                   "Всем"
                   ],
            item_id_getter=lambda x: x,
            id="grades",
            on_click=on_who_clicked,
        )),
        Cancel(Const("⏪ Назад")),
        state=PostSG.to_who
    ),
    Window(
        Format('<b>Пожалуйста, проверьте корректность введённых данных</b>\n'
               '<b>Пост:</b> {post}\n'),
        Column(
            Button(Const("Всё верно! ✅"), id="yes", on_click=on_post_ok_clicked),
            Back(Const("⏪ Назад"))
        ),
        parse_mode=ParseMode.HTML,
        state=PostSG.check,
        getter=get_data
    ),
    launch_mode=LaunchMode.SINGLE_TOP
)


async def answer_handler(m: Message, dialog: Dialog, manager: DialogManager):
    # Находим в Бд все ключи вопросов и проверяем содержатся ли они в сообщении
    for i in await Questions.filter().values_list("key",
                                                  flat=True):
        if m.text.find(str(i)) != -1:
            # Заменяем ключ вопроса в сообщении ответа на пустую строку
            manager.current_context().dialog_data["answer"] = m.text.replace(str(i), "")
            # Записываем номер ключа (тикета) в данные состояния
            manager.current_context().dialog_data["ticket"] = str(i)
            await manager.dialog().switch_to(AnswerSG.check)
            return
    await MyBot.bot.send_message(m.chat.id, "Вопроса с таким номером не существует")
    await manager.start(AdminSG.admin, mode=StartMode.RESET_STACK)


# Обрабатываем сообщение о подтверждении ответа на вопрос
async def on_answer_ok_clicked(c: CallbackQuery, button: Button, manager: DialogManager):
    await MyBot.bot.send_message(
        (await Questions.filter(key=manager.current_context().dialog_data["ticket"]).values_list("user_id_id",
                                                                                                 flat=True))[
            0], manager.current_context().dialog_data["answer"])
    # Находим в бд кому отправить сообщение, после чего - отправляем
    await Questions.filter(key=manager.current_context().dialog_data["ticket"]).update(is_answered=True)
    await MyBot.bot.send_message(CHAT_ID, "Ответ отправлен")
    await manager.done()
    await manager.bg().done()

# Ветка с ответом на вопрос
answer_dialog = Dialog(
    Window(
        Const("Please, answer"),
        MessageInput(answer_handler),
        Cancel(Const("⏪ Назад")),
        state=AnswerSG.answer
    ),
    Window(
        Format('<b>Пожалуйста, проверьте корректность введённых данных</b>\n'
               '<b>Тикет:</b> {ticket}\n'
               '<b>Ответ:</b> {answer}\n'),
        Column(
            Button(Const("Всё верно! ✅"), id="yes", on_click=on_answer_ok_clicked),
            Back(Const("⏪ Назад"))
        ),
        parse_mode=ParseMode.HTML,
        state=AnswerSG.check,
        getter=get_data
    ),
    launch_mode=LaunchMode.SINGLE_TOP
)

# Регистрируем все диалоги
MyBot.register_dialogs(root_admin_dialog, answer_dialog, post_dialog)
