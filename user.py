from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import ManagedDialogAdapterProto, LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Row, SwitchTo, Back, Start, Cancel
from aiogram_dialog.widgets.text import Const, Format

from database import ActiveUsers, Questions
from bot import MyBot
from config import Counter, NameCounter, CHAT_ID, programs_list


# PS: Надо подумать как редачить руками таблицы в docker, потому что нужно закинуть в таблицы
# список админов и инфу про программы


# Класс состояний регистрации пользователя
class RegistrationSG(StatesGroup):
    hi = State()
    name = State()
    grade = State()
    choose_grade = State()


async def start(m: Message, dialog_manager: DialogManager):
    if not (await ActiveUsers.filter(user_id=m.from_user.id).values_list("user_id")):
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


# Регистрируем хэндлер start
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
        SwitchTo(Const("Зарегистрироваться!"), id="fi", state=RegistrationSG.name),
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
    faq = State()
    ask = State()


# Класс состояний программ
class ProgramsSG(StatesGroup):
    choose_program = State()
    program_info = State()


# функция для получения данных из состояний
async def get_data_user(dialog_manager: DialogManager, **kwargs):
    return {
        'id': dialog_manager.current_context().dialog_data.get("id", None),
        'name': dialog_manager.current_context().dialog_data.get("name", None),
        'grade': dialog_manager.current_context().dialog_data.get("grade", None),
    }


# Если пользователь задал вопрос
async def quest_handler(m: Message, dialog: ManagedDialogAdapterProto, manager: DialogManager):
    count = Counter.get_count()
    name = (await ActiveUsers.filter(user_id=m.from_user.id).values_list("code_name", flat=True))[0]
    while await Questions.filter(key=count).values_list():
        count = Counter.get_count()  # Присваиваем вопросу идентификатор (цикл на тот случай если бота перезапустят)
    await MyBot.bot.send_message(CHAT_ID, f'<b>{str(count)}</b>' + '\n' + m.text + "\nОт: " + name, parse_mode="HTML")
    await Questions(key=count, user_id_id=m.from_user.id, question=m.text, is_answered=False).save()
    await MyBot.bot.send_message(m.from_user.id, 'Вопрос отправлен!')
    await manager.start(UserSG.menu, mode=StartMode.RESET_STACK)


# Диалог юзера (уже зарегистрирован)
user_menu_dialog = Dialog(
    Window(
        Format("Что тебя интересует?"),
        # Я думал сделать два диалога для шк и студ, но это тупо, поэтому нужно подумать как на этом этапе выгрузить
        # из бд текст для шк и студов по отдельности
        Start(Const("Программы для студентов 🧑‍🎓"), id="stud", state=ProgramsSG.choose_program),
        Start(Const("Программы для школьников 🎒"), id="sch", state=ProgramsSG.choose_program),
        SwitchTo(Const("Часто задаваемые вопросы 📍"), id="FAQ", state=UserSG.faq),
        SwitchTo(Const("Задать вопрос ❓"), id="qu", state=UserSG.ask),
        parse_mode=ParseMode.HTML,
        # getter=get_data_user,
        state=UserSG.menu
    ),
    Window(
        Const("Здесь будут часто задаваемые вопросы!"),
        Back(Const("⏪ Назад")),
        state=UserSG.faq
    ),
    Window(
        Const("Введите вопрос"),
        MessageInput(quest_handler),
        Back(Const("⏪ Назад")),
        state=UserSG.ask
    ),
    launch_mode=LaunchMode.ROOT
)


# функция для получения данных из состояний
async def get_data_programs(dialog_manager: DialogManager, **kwargs):
    return {
        'choose_program': dialog_manager.current_context().dialog_data.get("choose_program", None),
        'program_info': dialog_manager.current_context().dialog_data.get("program_info", None)
    }


async def on_program_clicked(c: ChatEvent, select: Select, manager: DialogManager, item_id: str):
    # Реализовать через бд
    manager.current_context().dialog_data["choose_program"] = item_id
    manager.current_context().dialog_data["program_info"] = programs_list[item_id]
    await manager.switch_to(ProgramsSG.program_info)

# Диалог программ будет заполняться в зависимости от того, кто юзер (шк, студ)
# На данный момент программы одинаковы для всех
# Так как через словарь сделать не получается, нужно через бд, где будет столбец для кого программа
programs = Dialog(
    Window(
        Format("<b>1. Летняя ИТ-школа КРОК</b>\n"
               "Бесплатный интенсив по погружению в одну из ИТ-профессий:"
               " от разработки и аналитики до маркетинга и продаж.\n"
               "В 2021 году студенты прошли обучение по 10 направлениям!\n\n"
               "<b>2. Лидерская программа</b>\n"
               "Это сообщество предприимчивых студентов. Мы даем возможности для прокачки,"
               " знакомим с экспертами из бизнеса и помогаем реализовывать инициативы в своем вузе.\n\n"
               "<b>3. Разработка приложений на языке С#</b>\n"
               "ПРАКТИЧЕСКИЙ КУРС ОТ КРОК\n"
               "Ты на практике разберешься в архитектуре приложений,"
               " погрузишься в особенности программирования на C#"
               " и создашь собственное приложение на Microsoft.NET Framework\n\n"
               "<b>4. ВВЕДЕНИЕ В ЯЗЫК JAVA И ПЛАТФОРМУ РАЗРАБОТКИ</b>\n"
               "Самые передовые практики и современные инструменты в мире корпоративной разработки на Java."
               " Эксперты и инженеры-практики по разработке и архитектуре ПО\n\n"
               "<b>5. Кейс-лаборатория КРОК</b>\n"
               "Закрой практику в университете, решая кейс под реальный бизнес-запрос. "
               "Тебя ждут 12 недель командной работы под руководством наставников\n\n"
               "<b>КЛИКАЙ НА КНОПКИ чтобы узнать подробнее</b>"),
        Row(Select(
            Format("{item}"),
            items=list(programs_list.keys()),
            item_id_getter=lambda x: x,
            id="grades",
            on_click=on_program_clicked
        )),
        Cancel(Const("⏪ Назад")),
        # getter=get_data_programs,
        parse_mode=ParseMode.HTML,
        state=ProgramsSG.choose_program
    ),
    Window(
        Format('{program_info}'),
        Back(Const("⏪ Назад")),
        getter=get_data_programs,
        parse_mode=ParseMode.HTML,
        state=ProgramsSG.program_info
    ),
    launch_mode=LaunchMode.SINGLE_TOP
)

# Регистрируем диалоги
MyBot.register_dialogs(registration_dialog, user_menu_dialog, programs)
