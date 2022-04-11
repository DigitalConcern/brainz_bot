import asyncio
from aiogram_dialog import DialogRegistry

import database
from config import dp
from user import usr_dialog, start
from admin import admin, root_admin_dialog, answer_dialog, post_dialog


async def main():
    dp.register_message_handler(start, text="/start", state="*")
    dp.register_message_handler(admin, text="/admin", state="*")
    registry = DialogRegistry(dp)
    registry.register(usr_dialog)
    registry.register(root_admin_dialog)
    registry.register(answer_dialog)
    registry.register(post_dialog)

    loop = asyncio.get_event_loop()
    loop.create_task(database.run())

    await dp.start_polling()


if __name__ == '__main__':
    asyncio.run(main())
