from sqlalchemy import text

from core.db_handler import db_handler


async def show_tables():
    """Show all tables in database"""
    async with db_handler.engine.begin() as conn:
        result = await conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))

        tables = result.fetchall()
        print("\n Database Tables:")
        for table in tables:
            print(f"  - {table[0]}")
