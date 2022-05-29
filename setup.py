import aiosqlite
import asyncio


async def setup_db():
    async with aiosqlite.connect("main.db") as db:
        await db.execute(
            """CREATE TABLE IF NOT EXISTS Challenges (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    challenge TEXT, 
                    author TEXT, 
                    accepted INTEGER
                )"""
        )
        await db.commit()


asyncio.run(setup_db())
