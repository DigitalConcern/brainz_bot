import os

from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode, ContentType

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Back, Column, Start, Cancel, Url
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from database import ActiveUsers, Questions
from bot import MyBot
from config import CHAT_ID, categories
from user import UserSG

from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message

from aiogram_dialog import Dialog, DialogManager, Window, StartMode
from aiogram_dialog.manager.protocols import LaunchMode
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.text import Const

from database import ActiveUsers
from bot import MyBot
from user import UserSG, RegistrationSG, registration_dialog, user_menu_dialog, programs_dialog_sch, \
    programs_dialog_std, question_dialog


async def start(m: Message, dialog_manager: DialogManager):
    if not (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id")):
        await dialog_manager.start(RegistrationSG.hi, mode=StartMode.RESET_STACK)
        # Если его нет в базе, то предлагаем зарегистрироваться
        dialog_manager.current_context().dialog_data["id"] = m.from_user.id
    elif (await ActiveUsers.filter(user_id=m.from_user.id).values_list("is_admin", flat=True))[0]:
        await dialog_manager.start(AdminSG.admin, mode=StartMode.RESET_STACK)
        # Если админ
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


# Регистрируем хэндлер start
MyBot.register_handler(method=start, commands=["start"])
# Регистрируем все диалоги

MyBot.register_dialogs(registration_dialog, user_menu_dialog, programs_dialog_sch, programs_dialog_std, question_dialog)


# В данном файле находится интерфейс админа


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
        'questioner': dialog_manager.current_context().dialog_data.get("questioner", None),
        'check': dialog_manager.current_context().dialog_data.get("check", None),
        'category': dialog_manager.current_context().dialog_data.get("category", None),
        'photo': dialog_manager.current_context().dialog_data.get("photo", None),
    }


# Корневой диалог админа
menu_admin_dialog = Dialog(
    Window(
        Const("Выбери действие 🤔"),
        Start(Const("Я хочу ответить на вопрос! ✅"), id="an", state=AnswerSG.answer),
        Start(Const("Я хочу создать пост! ✉️"), id="po", state=PostSG.post),
        Start(Const("Я хочу побыть юзером! ✉️"), id="uss", state=UserSG.admin_menu),
        Url(Const("Изменить информацию ℹ️"), Const("http://178.216.98.49/programs")),
        state=AdminSG.admin
    ),
    launch_mode=LaunchMode.ROOT
)


async def post_handler(m: Message, dialog: Dialog, manager: DialogManager):
    if m.text is None:
        manager.current_context().dialog_data["post"] = m.caption
        manager.current_context().dialog_data["photo"] = await MyBot.bot.get_file(m.photo[-1].file_id)
    else:
        manager.current_context().dialog_data["post"] = m.text
        manager.current_context().dialog_data["photo"] = None
    await manager.dialog().switch_to(PostSG.to_who)


# Выбор категории
async def on_who_clicked(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    manager.current_context().dialog_data["category"] = item_id
    await manager.dialog().switch_to(PostSG.check)


# Обрабатываем сообщение о подтверждении записи (поста)
async def on_post_ok_clicked(c: CallbackQuery, button: Button, manager: DialogManager):
    for grade in categories[manager.current_context().dialog_data["category"]]:
        for chel in await ActiveUsers.filter(grade=grade).values_list("user_id", flat=True):
            if manager.current_context().dialog_data["photo"] is None:
                await MyBot.bot.send_message(chel, manager.current_context().dialog_data["post"])
            else:
                await MyBot.bot.send_photo(chel, manager.current_context().dialog_data["photo"].file_id,
                                           caption=manager.current_context().dialog_data["post"])
    await MyBot.bot.send_message(CHAT_ID, "Пост отправлен")
    await manager.done()
    await manager.start(AdminSG.admin, mode=StartMode.NORMAL)


# Ветка с постом
post_dialog = Dialog(
    Window(
        Const("Пожалуйста, напишите текст поста"),
        MessageInput(post_handler, content_types=["text", "photo"]),
        Cancel(Const("⏪ Назад")),
        state=PostSG.post
    ),
    Window(
        Const("Кому отправить?"),
        Column(Select(
            Format("{item}"),
            items=["Школьникам",
                   "Студентам",
                   "Всем"
                   ],
            item_id_getter=lambda x: x,
            id="grades",
            on_click=on_who_clicked,
        )),
        Back(Const("⏪ Назад")),
        state=PostSG.to_who
    ),
    Window(
        Format('<b>Пожалуйста, проверьте корректность введённых данных</b>\n'
               '<b>Пост:</b> {post}\n'
               ),
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
            # Записываем имя юзера в данные состояния
            manager.current_context().dialog_data["questioner"] = (await Questions.filter(key=i).values_list(
                "user_id__code_name", flat=True))[0]
            await manager.dialog().switch_to(AnswerSG.check)
            return
    await MyBot.bot.send_message(m.chat.id, "Вопроса с таким номером не существует")
    await manager.done()
    await manager.start(AdminSG.admin, mode=StartMode.NORMAL)


# Обрабатываем сообщение о подтверждении ответа на вопрос
async def on_answer_ok_clicked(c: CallbackQuery, button: Button, manager: DialogManager):
    await MyBot.bot.send_message(
        (await Questions.filter(key=manager.current_context().dialog_data["ticket"]).values_list("user_id_id",
                                                                                                 flat=True))[0],
        manager.current_context().dialog_data["answer"])
    # Находим в бд кому отправить сообщение, после чего - отправляем
    await Questions.filter(key=manager.current_context().dialog_data["ticket"]).update(is_answered=True)
    await MyBot.bot.send_message(c.from_user.id, "Ответ отправлен")
    await manager.done()
    await manager.start(AdminSG.admin, mode=StartMode.NORMAL)


# Ветка с ответом на вопрос
answer_dialog = Dialog(
    Window(
        Const("Пожалуйста, напишите текст ответа на вопрос"),
        MessageInput(answer_handler),
        Cancel(Const("⏪ Назад")),
        state=AnswerSG.answer
    ),
    Window(
        Format('<b>Пожалуйста, проверьте корректность введённых данных</b>\n'
               '<b>Тикет:</b> {ticket}\n'
               '<b>Ответ:</b> {answer}\n'
               '<b>Получатель:</b> {questioner}\n'
               ),
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

MyBot.register_dialogs(menu_admin_dialog, answer_dialog, post_dialog)
