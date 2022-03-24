from aiogram import Dispatcher
from aiogram.types import Message

from web import services


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start, commands=["start"])

    dp.register_message_handler(send_my_id, commands=["id"])


async def start(message: Message):
    user, is_created = await services.add_user(
        tg_id=message.from_user.id,
        name=message.from_user.username
    )

    if is_created:
        await message.answer("You have successfully registered in the bot!")
    else:
        await message.answer("You are already registered in the bot!")


async def send_my_id(message: Message):
    await message.answer(
        f"User Id: <b>{message.from_user.id}</b>\n" f"Chat Id: <b>{message.chat.id}</b>"
    )