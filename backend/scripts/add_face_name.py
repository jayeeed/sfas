
import asyncio
import sys
from sqlalchemy import text
from app.db.session import async_session_maker

async def add_face_name_column():
    print("Migrating faces table: Adding 'name' column...")
    async with async_session_maker() as session:
        try:
            # Check if column exists
            try:
                await session.execute(text("SELECT name FROM faces LIMIT 1"))
                print("'name' column already exists.")
                return
            except Exception:
                pass # Column missing, proceed

            print("Adding 'name' column...")
            await session.execute(text("ALTER TABLE faces ADD COLUMN name VARCHAR(255)"))
            await session.commit()
            
            print("Successfully added 'name' column.")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            await session.rollback()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(add_face_name_column())
