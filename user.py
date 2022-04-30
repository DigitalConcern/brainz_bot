from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back, Start, Cancel, Url
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
    while await ActiveUsers.filter(code_name=count).all():
        count = NameCounter.get_count()
    await ActiveUsers(user_id=c.from_user.id,
                      password=None,
                      is_admin=False,
                      code_name=count,
                      user_name=c.from_user.first_name,
                      grade="12",
                      link=None
                      ).save()
    await MyBot.bot.send_message(manager.current_context().dialog_data["id"], "Поздравляю, вы зареганы!")
    await manager.done()
    await manager.start(UserSG.menu, mode=StartMode.RESET_STACK)


# Выбор класса обучения (для школьников)
async def on_grade_clicked(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    count = NameCounter.get_count()
    manager.current_context().dialog_data["grade"] = item_id
    while await ActiveUsers.filter(code_name=count).all():
        count = NameCounter.get_count()
    await ActiveUsers(user_id=c.from_user.id,
                      is_admin=False,
                      password=None,
                      code_name=count,
                      user_name=c.from_user.first_name,
                      grade=manager.current_context().dialog_data["grade"],
                      link=None
                      ).save()
    await MyBot.bot.send_message(manager.current_context().dialog_data["id"], "Поздравляю, вы зареганы!")
    await manager.done()
    await manager.start(UserSG.menu, mode=StartMode.RESET_STACK)


# Диалог регистрации пользователя
registration_dialog = Dialog(
    Window(
        Const("Привет! Мы – команда образовательного проекта Brainz, делаем около 50 программ и мероприятий в год: "
              "игры, кейсы, курсы, практика, акселератор."),
        SwitchTo(Const("Зарегистрироваться!"), id="fi", state=RegistrationSG.grade),
        state=RegistrationSG.hi
    ),
    Window(
        Const("А чем занимаешься ты?"),
        SwitchTo(Const("Школьник"), id="school", state=RegistrationSG.choose_grade),
        Button(Const("Студент"), id="student", on_click=on_student_clicked),
        Back(Const("⏪ Назад")),
        state=RegistrationSG.grade
    ),
    Window(
        Const("В каком классе ты учишься?"),
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
        Back(Const("⏪ Назад")),
        state=RegistrationSG.choose_grade
    ),
    launch_mode=LaunchMode.SINGLE_TOP
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
        Format("Это меню. Здесь ты можешь перейти в каталог образовательных программ для школьников или студентов, "
               "а если у тебя появились вопросы, то задать их команде Brainz."),
        Start(Const("Программы для студентов 🧑‍🎓"), id="stud", state=ProgramsSG_std.choose_program),
        Start(Const("Программы для школьников 🎒"), id="sch", state=ProgramsSG_sch.choose_program),
        Start(Const("Отправить вопрос в Brainz! ❓"), id="qu", state=QuestionsSG.choose),
        parse_mode=ParseMode.HTML,
        # getter=get_data_user,
        state=UserSG.menu
    ),
    Window(
        Format("Это меню. Здесь ты можешь перейти в каталог образовательных программ для школьников или студентов, "
               "а если у тебя появились вопросы, то задать их команде Brainz."),
        Start(Const("Программы для студентов 🧑‍🎓"), id="stud", state=ProgramsSG_std.choose_program),
        Start(Const("Программы для школьников 🎒"), id="sch", state=ProgramsSG_sch.choose_program),
        Start(Const("Отправить вопрос в Brainz! ❓"), id="qu", state=QuestionsSG.choose),
        Cancel(Const("⏪ Назад")),
        parse_mode=ParseMode.HTML,
        # getter=get_data_user,
        state=UserSG.admin_menu
    ),
    launch_mode=LaunchMode.SINGLE_TOP
)


# Если пользователь задал вопрос
async def quest_handler(m: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
    count = Counter.get_count()
    name = (await ActiveUsers.filter(user_id=m.from_user.id).values_list("code_name", flat=True))[0]
    while await Questions.filter(key=count).values_list():  # Пока в таблице есть вопрос с таким ключом - генерим его
        # заново
        count = Counter.get_count()  # Присваиваем вопросу идентификатор (цикл на тот случай если бота перезапустят)
    # Если текста нет, значит это фотка
    if m.text is None:
        await MyBot.bot.send_photo(CHAT_ID, (await MyBot.bot.get_file(m.photo[-1].file_id)).file_id, caption=f'<b>{str(count)}</b>' + '\n'
                                   + m.caption + "\nОт: " + name, parse_mode="HTML")
        await Questions(key=count, user_id_id=m.from_user.id, question=m.caption, is_answered=False).save()

    else:
        await MyBot.bot.send_message(CHAT_ID, f'<b>{str(count)}</b>' + '\n' + m.text + "\nОт: " + name,
                                     parse_mode="HTML")
        await Questions(key=count, user_id_id=m.from_user.id, question=m.text, is_answered=False).save()

    await MyBot.bot.send_message(m.from_user.id, 'Наш сотрудник уже спешит помочь тебе, ответ придет прямо в бот.')
    await manager.done()

    if (await ActiveUsers.filter(user_id=m.from_user.id).values_list("is_admin", flat=True))[0]:
        await manager.start(UserSG.admin_menu)
    else:
        await manager.start(UserSG.menu, mode=StartMode.RESET_STACK)


# Диалог с вопросами
question_dialog = Dialog(
    Window(
        Format("Прежде, чем отправить вопрос, убедись, пожалуйста, что ответа нет в FAQ."),
        SwitchTo(Const("Ответы на частые вопросы"), id="faq", state=QuestionsSG.faq),
        SwitchTo(Const("Всё равно задать вопрос."), id="ask", state=QuestionsSG.ask),
        Cancel(Const("⏪ Назад")),
        parse_mode=ParseMode.HTML,
        state=QuestionsSG.choose

    ),
    Window(
        Const("Здесь будут часто ответы на часто задаваемые вопросы!"),
        Back(Const("⏪ Назад")),
        state=QuestionsSG.faq
    ),
    Window(
        Const("Отправь в бот сообщение с вопросом – мы перешлем его сотруднику (но только одно, если у тебя появятся "
              "новые вопросы, заново перейди по кнопке из меню)"),
        MessageInput(quest_handler, content_types=["text", "photo"]),
        Back(Const("⏪ Назад")),
        state=QuestionsSG.ask
    ),
    launch_mode=LaunchMode.SINGLE_TOP
)


# функция для получения данных из состояний
async def get_data_programs(dialog_manager: DialogManager, **kwargs):
    # Достаем из базы тексты всех программ
    programs_students = list(await Programs.filter(category="students").order_by("key").values_list("description", flat=True))
    names_students = list(await Programs.filter(category="students").order_by("key").values_list("name", flat=True))
    keys_students = list(await Programs.filter(category="students").order_by("key").values_list("key", flat=True))
    programs_school = list(await Programs.filter(category="school").order_by("key").values_list("description", flat=True))
    names_school = list(await Programs.filter(category="school").order_by("key").values_list("name", flat=True))
    keys_school = list(await Programs.filter(category="school").order_by("key").values_list("key", flat=True))
    preview_students = ''
    preview_school = ''

    for i in range(len(programs_students)):
        preview_students += f'<b>{keys_students[i]}. {names_students[i]}</b>\n{programs_students[i]}\n\n'

    for i in range(len(programs_school)):
        preview_school = f'<b>{keys_school[i]}. {names_school[i]}</b>\n{programs_school[i]}\n\n'

    return {
        'programs_list_student': preview_students,
        'programs_list_school': preview_school,
        'choose_program': dialog_manager.current_context().dialog_data.get("choose_program", None),
        'program_info': dialog_manager.current_context().dialog_data.get("program_info", None),
        'keys_students': keys_students,
        'keys_school': keys_school,
        'link': dialog_manager.current_context().dialog_data.get("link", None),
    }


async def on_program_clicked_std(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    # Реализовано через БД
    manager.current_context().dialog_data["choose_program"] = item_id
    manager.current_context().dialog_data["program_info"] = "".join(
        await Programs.filter(key=int(item_id), category="students").values_list("info", flat=True))
    manager.current_context().dialog_data["link"] = "".join(
        await Programs.filter(key=int(item_id), category="students").values_list("link", flat=True))
    await manager.switch_to(ProgramsSG_std.program_info)


async def on_program_clicked_sch(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    # Реализовано через БД
    manager.current_context().dialog_data["choose_program"] = item_id
    manager.current_context().dialog_data["program_info"] = "".join(
        await Programs.filter(key=int(item_id), category="school").values_list("info", flat=True))
    manager.current_context().dialog_data["link"] = "".join(
        await Programs.filter(key=int(item_id), category="school").values_list("link", flat=True))
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
        # Button(Const("⏪ Назад"), id="smrt_back_quest", on_click=smrt_back_is_admin),
        Cancel(Const("⏪ Назад")),
        getter=get_data_programs,
        parse_mode=ParseMode.HTML,
        state=ProgramsSG_sch.choose_program
    ),
    Window(
        Format('{program_info}'),
        Url(
            Const("Зарегистрироваться!"),
            Format('{link}'),
        ),
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
            items="keys_students",
            item_id_getter=lambda x: x,
            id="grades",
            on_click=on_program_clicked_std
        )),
        # Button(Const("⏪ Назад"), id="smrt_back_quest", on_click=smrt_back_is_admin),
        Cancel(Const("⏪ Назад")),
        getter=get_data_programs,
        parse_mode=ParseMode.HTML,
        state=ProgramsSG_std.choose_program
    ),
    Window(
        Format('{program_info}'),
        Url(
            Const("Зарегистрироваться!"),
            Format('{link}'),
        ),
        Back(Const("⏪ Назад")),
        getter=get_data_programs,
        parse_mode=ParseMode.HTML,
        state=ProgramsSG_std.program_info
    ),
    launch_mode=LaunchMode.SINGLE_TOP
)
