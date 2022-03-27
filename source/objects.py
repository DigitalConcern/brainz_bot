import asyncio
import logging
import os
from multiprocessing import Process
from django.core.asgi import get_asgi_application
import uvicorn
import telebot
from bot.config import *
import time

logging.basicConfig(level=logging.DEBUG)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "based.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# load_dotenv(BASE_DIR / "config" / ".env")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bot = telebot.TeleBot(TOKEN)


class MyServer:
    app = get_asgi_application()

    config = uvicorn.Config(host='178.216.98.49', app=app, loop=loop, port=80)
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
    bot.polling(none_stop=True)
    time.sleep(60)


if __name__ == "__main__":
    run_app()
