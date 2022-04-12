import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram_dialog import DialogRegistry

from user import usr_dialog, start
from admin import admin, root_admin_dialog, answer_dialog, post_dialog
from config import API_TOKEN
from bot import bot,dp


async def run_bot():
    dp.register_message_handler(start, text="/start", state="*")
    dp.register_message_handler(admin, text="/admin", state="*")

    registry = DialogRegistry(dp)

    registry.register(usr_dialog)
    registry.register(root_admin_dialog)
    registry.register(answer_dialog)
    registry.register(post_dialog)

    await dp.start_polling()
