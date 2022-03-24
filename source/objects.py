import asyncio
import logging
import os
from multiprocessing import Process
from django.core.asgi import get_asgi_application
import uvicorn
import telebot
from bot.config import *

logging.basicConfig(level=logging.DEBUG)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "based.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# load_dotenv(BASE_DIR / "config" / ".env")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bot = telebot.TeleBot(TOKEN)

def MyBot():
    from source.web import services

    @bot.message_handler(commands=["start"])
    def start(message):
        user, is_created = services.add_user(
            tg_id=message.from_user.id,
            username=message.from_user.username
        )

        if is_created:
            bot.send_message(message.from_user.id, "You have successfully registered in the bot!")
        else:
            bot.send_message(message.from_user.id, "You are already registered in the bot!")

    @bot.message_handler(commands=["id"])
    def send_my_id(message):
        bot.send_message(message.from_user.id,
                         f"User Id: <b>{message.from_user.id}</b>\n" f"Chat Id: <b>{message.chat.id}</b>",
                         parse_mode="HTML")

    bot.polling(none_stop=True)


class MyServer:
    app = get_asgi_application()

    config = uvicorn.Config(app=app, loop=loop, port=8001)
    server = uvicorn.Server(config=config)

    @classmethod
    def run(cls):
        # asyncio.run(cls.on_startup())
        asyncio.run(cls.server.serve())
        asyncio.run(cls.on_shutdown())

    # @staticmethod
    # async def on_startup() -> None:
    #     InjectMiddleware.inject_params = dict(bot=MyBot.bot)
    #
    #     await register_apps()

    @staticmethod
    async def on_shutdown() -> None:
        pass


def run_app():
    server = Process(target=MyServer.run)
    server.start()
    MyBot()


if __name__ == "__main__":
    run_app()
