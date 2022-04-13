import asyncio
from database import loop_db
from bot import MyBot
import admin
import user


async def main():
    await loop_db()
    await MyBot.run_bot()


if __name__ == '__main__':
    asyncio.run(main())
