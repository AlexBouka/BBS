import asyncio

from core.database import Base
from core.db_handler import db_handler


async def recreate_database():
    async with db_handler.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        print("======== All tables dropped. ========")

        await conn.run_sync(Base.metadata.create_all)
        print("======== All tables created. ========")


if __name__ == "__main__":
    asyncio.run(recreate_database())
