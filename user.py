from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode, ReplyKeyboardMarkup, KeyboardButton

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back, Start, Cancel
from aiogram_dialog.widgets.text import Const, Format

from database import ActiveUsers, Questions, Programs
from bot import MyBot
from config import Counter, NameCounter, CHAT_ID


# PS: Надо подумать как редачить руками таблицы в docker, потому что нужно закинуть в таблицы
# список админов и инфу про программы


# Класс состояний регистрации пользователя
class RegistrationSG(StatesGroup):
    hi = State()
    grade = State()
    choose_grade = State()


# Если студент нажал кнопку "студент"
async def on_student_clicked(c: CallbackQuery, button: Button, manager: DialogManager):
    count = NameCounter.get_count()
    manager.current_context().dialog_data["grade"] = "12"
    while await ActiveUsers.filter(code_name=count).values_list():
        count = NameCounter.get_count()
    await ActiveUsers(user_id=manager.current_context().dialog_data["id"],
                      is_admin=False,
                      code_name=count,
                      user_name=c.from_user.first_name,
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
                      is_admin=False,
                      code_name=count,
                      user_name=manager.current_context().dialog_data["name"],
                      grade=manager.current_context().dialog_data["grade"]
                      ).save()
    await MyBot.bot.send_message(manager.current_context().dialog_data["id"], "Поздравляю, вы зареганы!")
    await manager.done()
    await manager.start(UserSG.menu, mode=StartMode.RESET_STACK)


# Диалог регистрации пользователя
registration_dialog = Dialog(
    Window(
        Const("Greetings! Мы - КРОК, пройди пжж регистрацию"),
        SwitchTo(Const("Зарегистрироваться!"), id="fi", state=RegistrationSG.grade),
        state=RegistrationSG.hi
    ),
    Window(
        Const("Ты школьник или студент?"),
        SwitchTo(Const("Школьник"), id="school", state=RegistrationSG.choose_grade),
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


# Класс состояний пользователя
class UserSG(StatesGroup):
    menu = State()
    admin_menu = State()


# Класс состояний программ
class ProgramsSG_std(StatesGroup):
    choose_program = State()
    program_info = State()


# Класс состояний программ
class ProgramsSG_sch(StatesGroup):
    choose_program = State()
    program_info = State()


# Класс состояний диалога вопросов
class QuestionsSG(StatesGroup):
    choose = State()
    faq = State()
    ask = State()


# функция для получения данных из состояний
async def get_data_user(dialog_manager: DialogManager, **kwargs):
    return {
        'id': dialog_manager.current_context().dialog_data.get("id", None),
        'name': dialog_manager.current_context().dialog_data.get("name", None),
        'grade': dialog_manager.current_context().dialog_data.get("grade", None),
    }


# Диалог юзера (уже зарегистрирован)
user_menu_dialog = Dialog(
    Window(
        Format("Что тебя интересует?"),
        # Я думал сделать два диалога для шк и студ, но это тупо, поэтому нужно подумать как на этом этапе выгрузить
        # из бд текст для шк и студов по отдельности
        Start(Const("Программы для студентов 🧑‍🎓"), id="stud", state=ProgramsSG_std.choose_program),
        Start(Const("Программы для школьников 🎒"), id="sch", state=ProgramsSG_sch.choose_program),
        Start(Const("Задать вопрос ❓"), id="qu", state=QuestionsSG.choose),
        parse_mode=ParseMode.HTML,
        # getter=get_data_user,
        state=UserSG.menu
    ),
    Window(
        Format("Что тебя интересует?"),
        # Я думал сделать два диалога для шк и студ, но это тупо, поэтому нужно подумать как на этом этапе выгрузить
        # из бд текст для шк и студов по отдельности
        Start(Const("Программы для студентов 🧑‍🎓"), id="stud", state=ProgramsSG_std.choose_program),
        Start(Const("Программы для школьников 🎒"), id="sch", state=ProgramsSG_sch.choose_program),
        Start(Const("Задать вопрос ❓"), id="qu", state=QuestionsSG.choose),
        Cancel(Const("⏪ Назад")),
        parse_mode=ParseMode.HTML,
        # getter=get_data_user,
        state=UserSG.admin_menu
    ),
    launch_mode=LaunchMode.STANDARD
)


# Если пользователь задал вопрос
async def quest_handler(m: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
    count = Counter.get_count()
    name = (await ActiveUsers.filter(user_id=m.from_user.id).values_list("code_name", flat=True))[0]
    while await Questions.filter(key=count).values_list():
        count = Counter.get_count()  # Присваиваем вопросу идентификатор (цикл на тот случай если бота перезапустят)
    await MyBot.bot.send_message(CHAT_ID, f'<b>{str(count)}</b>' + '\n' + m.text + "\nОт: " + name, parse_mode="HTML")
    await Questions(key=count, user_id_id=m.from_user.id, question=m.text, is_answered=False).save()
    await MyBot.bot.send_message(m.from_user.id, 'Вопрос отправлен!')

    if (await ActiveUsers.filter(user_id=m.from_user.id).values_list("is_admin", flat=True))[0]:
        await manager.start(UserSG.admin_menu, mode=StartMode.RESET_STACK)
    else:
        await manager.start(UserSG.menu, mode=StartMode.RESET_STACK)


async def smrt_back_is_admin(c: CallbackQuery, button: Button, manager: DialogManager):
    if (await ActiveUsers.filter(user_id=c.from_user.id).values_list("is_admin", flat=True))[0]:
        await manager.switch_to(UserSG.admin_menu)
    else:
        await manager.switch_to(UserSG.menu)

# Диалог с вопросами
question_dialog = Dialog(
    Window(
        Format("Проверь список ответов и вопросов!\n"
               "Возможно, на твой вопрос уже есть <b>ответ!</b>"),
        SwitchTo(Const("Ответы на частые вопросы"), id="faq", state=QuestionsSG.faq),
        SwitchTo(Const("Задать вопрос эксперту"), id="ask", state=QuestionsSG.ask),
        Button(Const("⏪ Назад"), id="smrt_back_quest", on_click=smrt_back_is_admin),
        parse_mode=ParseMode.HTML,
        state=QuestionsSG.choose

    ),
    Window(
        Const("Здесь будут часто ответы на часто задаваемые вопросы!"),
        SwitchTo(Const("⏪ Назад"), id="smrt_back_faq", state=QuestionsSG.choose),
        state=QuestionsSG.faq
    ),
    Window(
        Const("Введите вопрос"),
        MessageInput(quest_handler),
        SwitchTo(Const("⏪ Назад"), id="smrt_back_ask", state=QuestionsSG.choose),
        state=QuestionsSG.ask
    ),
    launch_mode=LaunchMode.EXCLUSIVE
)


# функция для получения данных из состояний
async def get_data_programs(dialog_manager: DialogManager, **kwargs):
    return {
        # Достаем из базы тексты всех программ
        'programs_list_student': "\n\n".join(
            await Programs.filter(category="students").values_list("description", flat=True)),
        'programs_list_school': "\n\n".join(
            await Programs.filter(category="school").values_list("description", flat=True)),
        'choose_program': dialog_manager.current_context().dialog_data.get("choose_program", None),
        'program_info': dialog_manager.current_context().dialog_data.get("program_info", None),
        'keys_student': list(await Programs.filter(category="students").values_list("key", flat=True)),
        'keys_school': list(await Programs.filter(category="school").values_list("key", flat=True))
    }


async def on_program_clicked_std(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    # Реализовано через БД
    manager.current_context().dialog_data["choose_program"] = item_id
    manager.current_context().dialog_data["program_info"] = "".join(
        await Programs.filter(key=int(item_id), category="students").values_list("info", flat=True))
    await manager.switch_to(ProgramsSG_std.program_info)


async def on_program_clicked_sch(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    # Реализовано через БД
    manager.current_context().dialog_data["choose_program"] = item_id
    manager.current_context().dialog_data["program_info"] = "".join(
        await Programs.filter(key=int(item_id), category="school").values_list("info", flat=True))
    await manager.switch_to(ProgramsSG_sch.program_info)


# Диалог программ будет заполняться в зависимости от того, кто юзер (шк, студ)
# На данный момент программы одинаковы для всех
# Так как через словарь сделать не получается, нужно через бд, где будет столбец для кого программа
programs_dialog_sch = Dialog(
    Window(
        Format("{programs_list_school}"),
        Row(Select(
            Format("{item}"),
            items="keys_school",
            item_id_getter=lambda x: x,
            id="grades",
            on_click=on_program_clicked_sch
        )),
        Button(Const("⏪ Назад"), id="smrt_back_quest", on_click=smrt_back_is_admin),
        getter=get_data_programs,
        parse_mode=ParseMode.HTML,
        state=ProgramsSG_sch.choose_program
    ),
    Window(
        Format('{program_info}'),
        Back(Const("⏪ Назад")),
        getter=get_data_programs,
        parse_mode=ParseMode.HTML,
        state=ProgramsSG_sch.program_info
    ),
    launch_mode=LaunchMode.SINGLE_TOP
)

programs_dialog_std = Dialog(
    Window(
        Format("{programs_list_student}"),
        Row(Select(
            Format("{item}"),
            items="keys_student",
            item_id_getter=lambda x: x,
            id="grades",
            on_click=on_program_clicked_std
        )),
        Button(Const("⏪ Назад"), id="smrt_back_quest", on_click=smrt_back_is_admin),
        getter=get_data_programs,
        parse_mode=ParseMode.HTML,
        state=ProgramsSG_std.choose_program
    ),
    Window(
        Format('{program_info}'),
        Back(Const("⏪ Назад")),
        getter=get_data_programs,
        parse_mode=ParseMode.HTML,
        state=ProgramsSG_std.program_info
    ),
    launch_mode=LaunchMode.SINGLE_TOP
)

# Регистрируем диалоги
MyBot.register_dialogs(registration_dialog, user_menu_dialog, programs_dialog_sch, programs_dialog_std, question_dialog)

#                "<b>4. ВВЕДЕНИЕ В ЯЗЫК JAVA И ПЛАТФОРМУ РАЗРАБОТКИ</b>\n"
#                "Самые передовые практики и современные инструменты в мире корпоративной разработки на Java."
#                " Эксперты и инженеры-практики по разработке и архитектуре ПО\n\n"
#                "<b>5. Кейс-лаборатория КРОК</b>\n"
#                "Закрой практику в университете, решая кейс под реальный бизнес-запрос. "
#                "Тебя ждут 12 недель командной работы под руководством наставников\n\n"
#                "<b>КЛИКАЙ НА КНОПКИ чтобы узнать подробнее</b>"
