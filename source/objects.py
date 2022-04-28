import asyncio
import logging
import os
import uvicorn

from multiprocessing import Process
from django.core.asgi import get_asgi_application

logging.basicConfig(level=logging.DEBUG)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "based.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# load_dotenv(BASE_DIR / "config" / ".env")

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)


class MyServer:
    app = get_asgi_application()

    # config = uvicorn.Config(host='0.0.0.0', app=app, loop=loop, port=8080)
    config = uvicorn.Config(app=app, loop=loop, port=8001)
    server = uvicorn.Server(config=config)

    @classmethod
    def run(cls):
        # asyncio.run(cls.on_startup())
        asyncio.run(cls.server.serve())
        # asyncio.run(cls.on_shutdown())

    # @staticmethod
    # async def on_startup() -> None:
    #     InjectMiddleware.inject_params = dict(bot=MyBot.bot)
    #
    #     await register_apps()

    # @staticmethod
    # async def on_shutdown() -> None:
    #     pass


def run_app():
    from django.contrib.auth.models import User
    from sesame import utils
    from web import models
    email = "den"
    user = User.objects.get(username=email)
    login_token = utils.get_parameters(user)
    login_link = "http://127.0.0.1:8001/?sesame={}".format(login_token["sesame"])
    print(login_link)
    newlink = models.Links()
    newlink.link = login_link
    newlink.save()

    server = Process(target=MyServer.run)
    server.start()


if __name__ == "__main__":
    run_app()
