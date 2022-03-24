import asyncio
import logging
import os, sys, time
from multiprocessing import Process
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "based.settings")

import uvicorn
from telebot import TeleBot
from bot import config
from web import services

logging.basicConfig(level=logging.DEBUG)

os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# load_dotenv(BASE_DIR / "config" / ".env")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


class MyBot:
    bot = TeleBot(token=config.TOKEN, parse_mode="HTML")

    @classmethod
    def run(cls):
        while True:
            try:
                cls.bot.polling(none_stop=True)
            except:
                print('roflan-ebalo 😎')
                logging.error('error: {}'.format(sys.exc_info()[0]))
                time.sleep(5)

    @staticmethod
    @bot.message_handler(commands=['start'])
    def start(message):
        user, is_created = services.add_user(
            tg_id=message.from_user.id,
            name=message.from_user.username
        )

        if is_created:
            message.answer("You have successfully registered in the bot!")
        else:
            message.answer("You are already registered in the bot!")

    @staticmethod
    @bot.message_handler(commands=['id'])
    def send_my_id(message):
        message.answer(
            f"User Id: <b>{message.from_user.id}</b>\n" f"Chat Id: <b>{message.chat.id}</b>"
        )
    # @staticmethod
    # async def on_startup(dp: Dispatcher):
    #     await register_apps(dp)

    # @staticmethod
    # async def on_shutdown(dp: Dispatcher):
    #     pass


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
    bot = Process(target=MyBot.run)
    server = Process(target=MyServer.run)

    bot.start()
    server.start()


if __name__ == "__main__":
    run_app()
