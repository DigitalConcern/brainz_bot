import asyncio
from database import loop_db
from bot import MyBot
from admin import admin, root_admin_dialog, answer_dialog, post_dialog
from user import usr_dialog, start


async def main():
    await loop_db()
    await MyBot.run_bot()

if __name__ == '__main__':
    asyncio.run(main())
