import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram_dialog import DialogRegistry

from user import usr_dialog, start
from admin import admin, root_admin_dialog, answer_dialog, post_dialog
from config import API_TOKEN

# logging.basicConfig(level=logging.INFO)
# storage = MemoryStorage()
# bot = Bot(token=API_TOKEN)
# dp = Dispatcher(bot, storage=storage)


class MyBot:
    storage = MemoryStorage()
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher(bot, storage=storage)

    @staticmethod
    async def run_bot(dispatcher: Dispatcher):
        logging.basicConfig(level=logging.INFO)
        dispatcher.register_message_handler(start, text="/start", state="*")
        dispatcher.register_message_handler(admin, text="/admin", state="*")

        registry = DialogRegistry(dispatcher)

        registry.register(usr_dialog)
        registry.register(root_admin_dialog)
        registry.register(answer_dialog)
        registry.register(post_dialog)

        await dispatcher.start_polling()
