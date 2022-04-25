from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, ParseMode

from aiogram_dialog import Dialog, DialogManager, Window, ChatEvent, StartMode
from aiogram_dialog.manager.protocols import LaunchMode
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Select, Back, Column, Start, Cancel
from aiogram_dialog.widgets.text import Const, Format

from database import ActiveUsers, Questions, Programs
from bot import MyBot
from config import CHAT_ID
from user import UserSG, RegistrationSG
from admin import AdminSG


class RootAdminSG(StatesGroup):
    root_admin = State()


async def start(m: Message, dialog_manager: DialogManager):
    # try:
    #     await Programs(
    #         id=1,
    #         key=1,
    #         name="Летняя ИТ-школа КРОК",
    #         description="<b>1. Летняя ИТ-школа КРОК</b> – бесплатный интенсив по погружению в одну из ИТ-профессий:"
    #                     " от разработки и аналитики до маркетинга и продаж."
    #                     "В 2021 году студенты прошли обучение по 10 направлениям!",
    #         info="<b>Летняя ИТ-школа КРОК</b> – бесплатный интенсив по погружению в одну из ИТ-профессий: от разработки и "
    #              "аналитики до маркетинга и продаж.\nВ 2021 году студенты прошли обучение по 10 направлениям! Каждое из "
    #              "них – двухнедельное обучение. За это время ты перенимаешь опыт у экспертов-практиков, отрабатываешь "
    #              "полученные компетенции на командном кейсе и получаешь возможность начать карьеру сразу по завершении "
    #              "Школы.\nЗдесь не обучают с нуля – мы стараемся собрать сильную группу, в которой каждый студент усилит "
    #              "другого и поможет вырасти профессионально за очень короткий срок. Благодаря этому 53 участника Школы "
    #              "начали свою карьеру летом 2021 года!",
    #         category="students",
    #         is_active=True,
    #         link="https://schoolcroc.ru/",
    #     ).save()
    #
    #     await Programs(
    #         id=2,
    #         key=2,
    #         name="Лидерская программа",
    #         description="<b>2. Лидерская программа</b> — это сообщество предприимчивых студентов."
    #                     " Мы даем возможности для прокачки, знакомим с экспертами из бизнеса"
    #                     " и помогаем реализовывать инициативы в своем вузе.",
    #         info="<b>Из чего состоит Лидерская программа?</b>\n\n"
    #              "<b>Среда развития</b>\n"
    #              "Ты в разных форматах прокачаешь soft skills, познакомишься с техническими экспертами и топ-менеджерами "
    #              "КРОК, узнаешь о проектах, технологиях и трендах в ИТ, вместе с наставником построишь свой трек "
    #              "личностного развития. А еще реализуешь свою инициативу в партнерстве с КРОК.\n"
    #              "<b>Амбассадорство</b>\n"
    #              "Каждый год КРОК проводит более 50 образовательных программ и мероприятий. Но найти себя хотят сотни "
    #              "тысяч студентов по всей России — в этом нужна твоя помощь. Ты станешь амбассадором КРОК и попадешь на "
    #              "лучшие профтусовки, митапы и карьерные ивенты не только в роли участника, но и организатора.\n"
    #              "<b>Сообщество лидеров</b>\n"
    #              "Мы соберем студентов, готовых развиваться и менять образовательную среду. Ты встретишься с такими же "
    #              "амбициозными, увлеченными и талантливыми лидерами, чтобы, обмениваясь опытом, создавать крутые проекты.\n"
    #              "<b>Карьерный буст</b>\n"
    #              "Ты получишь доступ к экспертизе HR-команды КРОК, которая поможет найти карьерную траекторию и "
    #              "расскажет, как успешно пройти отбор в ИТ-компанию. А еще участие в программе — это возможность добавить "
    #              "проекты в свое портфолио.\n",
    #         category="students",
    #         is_active=True,
    #         link="https://studleader.ru/",
    #     ).save()
    #
    #     await Programs(
    #         id=3,
    #         key=1,
    #         name="Школа IT-решений",
    #         description="<b>1. Школа IT-решений</b>\nКоманда школьников готова на все, чтобы их ИТ-проект принес пользу. "
    #                     "Новый сезон большой франшизы о вызовах, дружбе и технологиях. ",
    #         info="<b>Из чего состоит ШИР?</b>\n"
    #              "\n<b>Полное погружение</b>\nДрама, ситком, боевик, шпионский детектив — ты пройдешь по всем жанрам "
    #              "работы над ИТ-проектом. "
    #              "\n<b>Создание реального продукта</b>\nКак понять, что нашел своего пользователя? Он попытается тебя "
    #              "убить, но твоя команда все равно сделает его жизнь лучше. "
    #              "\n<b>Работа в команде</b>\n«Ковальски, варианты!» станет привычной фразой к середине сезона. Успех или "
    #              "поражение — главное вместе улыбаться и махать. "
    #              "\n<b>Знакомство с экспертами</b>\nУ каждого главного героя есть тактика, которой нужно придерживаться. "
    #              "Например, знакомиться со всеми экспертами из ИТ-компаний, чтобы открыть пасхалку в конце "
    #              "\n<b>Увлекательные сюжетные повороты</b>\nСценарий расписан на полгода: с сетапами, панчлайнами и "
    #              "клиффхангерами. От серии к серии ты будешь получать только актуальные практические знания. "
    #              "\n<b>Филлеры</b>\nКак и в любой франшизе, есть дополнительный материал, не связанный с основным "
    #              "сюжетом. Это онлайн-лекции, мемы и тусовки для своих",
    #         category="school",
    #         is_active=True,
    #         link="https://itsolschool.ru/",
    #     ).save()
    # except:
    #     pass
    #
    # try:
    #     await ActiveUsers(user_id=380781069,
    #                       is_admin=True,
    #                       code_name="#green10",
    #                       user_name="den",
    #                       grade="12"
    #                       ).save()
    #     await ActiveUsers(user_id=678197278,
    #                       is_admin=True,
    #                       code_name="#red10",
    #                       user_name="miha",
    #                       grade="12"
    #                       ).save()
    # except:
    #     pass


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
