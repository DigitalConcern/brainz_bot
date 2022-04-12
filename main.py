import asyncio
from database import loop_db
from bot import run_bot


async def main():
    await loop_db()
    await run_bot()

if __name__ == '__main__':
    asyncio.run(main())
