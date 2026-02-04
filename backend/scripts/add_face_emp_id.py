
import asyncio
import sys
from sqlalchemy import text
from app.db.session import async_session_maker

async def add_face_emp_id_column():
    print("Migrating faces table: Adding 'emp_id' column...")
    async with async_session_maker() as session:
        try:
            # Check if column exists
            try:
                await session.execute(text("SELECT emp_id FROM faces LIMIT 1"))
                print("'emp_id' column already exists.")
                return
            except Exception:
                pass # Column missing, proceed

            print("Adding 'emp_id' column...")
            await session.execute(text("ALTER TABLE faces ADD COLUMN emp_id VARCHAR(255)"))
            
            # Create index for emp_id
            await session.execute(text("CREATE INDEX ix_faces_emp_id ON faces (emp_id)"))
            
            await session.commit()
            
            print("Successfully added 'emp_id' column.")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            await session.rollback()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(add_face_emp_id_column())
