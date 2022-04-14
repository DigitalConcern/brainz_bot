import asyncio
from database import loop_db
from bot import MyBot
import admin
import user
from database import Programs


async def main():
    await Programs(key=1,
                   text="<b>1. Летняя ИТ-школа КРОК</b>\n"
                        "Бесплатный интенсив по погружению в одну из ИТ-профессий:"
                        " от разработки и аналитики до маркетинга и продаж.\n"
                        "В 2021 году студенты прошли обучение по 10 направлениям!\n\n",
                   is_student="All"
                   ).save()

    await loop_db()
    await MyBot.run_bot()
    await MyBot.bot.send_message("-721759162", Programs.filter().values_list("text", flat=True)[0])


if __name__ == '__main__':
    asyncio.run(main())
