
import asyncio
import sys
from sqlalchemy import text
from app.db.session import async_session_maker

async def migrate_roles():
    print("Starting role migration...")
    async with async_session_maker() as session:
        try:
            # Check all roles
            result = await session.execute(text("SELECT DISTINCT role FROM users"))
            roles = [r[0] for r in result.fetchall()]
            print(f"Current roles in DB: {roles}")
            
            # Fix legacy or uppercase roles
            # Convert 'STUDENT', 'student', 'EMPLOYEE', 'employee' -> 'user'
            # Convert 'ADMIN' -> 'admin' (if needed)
            
            await session.execute(text("UPDATE users SET role = 'user' WHERE lower(role) IN ('student', 'employee')"))
            await session.execute(text("UPDATE users SET role = 'admin' WHERE role = 'ADMIN'"))
            await session.execute(text("UPDATE users SET role = 'user' WHERE role = 'USER'"))
            
            await session.commit()
            print("Migration queries executed.")
            
        except Exception as e:
            print(f"Error during migration: {e}")
            await session.rollback()

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(migrate_roles())
