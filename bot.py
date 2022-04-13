import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram_dialog import DialogRegistry
from config import API_TOKEN


# logging.basicConfig(level=logging.INFO)
# storage = MemoryStorage()
# bot = Bot(token=API_TOKEN)
# dp = Dispatcher(bot, storage=storage)


class MyBot:
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)

    @classmethod
    async def run_bot(cls):
        logging.basicConfig(level=logging.INFO)
        await cls.dp.start_polling()

    @classmethod
    def register_handler(cls, **kwargs):
        cls.dp.register_message_handler(kwargs["method"], text=kwargs["text"], state=kwargs["state"])

    @classmethod
    def register_dialogs(cls, *args):
        registry = DialogRegistry(cls.dp)
        for dialog in args:
            registry.register(dialog)
