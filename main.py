import asyncio
from database import loop_db
from bot import MyBot


async def main():
    await loop_db()
    await MyBot.run_bot(MyBot.dp)

if __name__ == '__main__':
    asyncio.run(main())
