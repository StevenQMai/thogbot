import aiosqlite
import asyncio
from datetime import datetime
import pytz

class Database:
    def __init__(self):
        self.db_path = "tasks.db"
        asyncio.create_task(self._init_db())

    async def _init_db(self):
        """Initialize the database with required tables."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    due_date TEXT,
                    priority TEXT CHECK(priority IN ('low', 'medium', 'high')),
                    status TEXT CHECK(status IN ('pending', 'in_progress', 'completed')),
                    created_by INTEGER NOT NULL,
                    assigned_to INTEGER,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(title, description, due_date, created_by)
                )
            """)
            await db.commit()

    async def add_task(self, title, description, due_date, priority, created_by, assigned_to=None):
        """Add a new task to the database."""
        now = datetime.now(pytz.UTC).isoformat()
        print(f"Adding task: {title}")  # Debug log
        async with aiosqlite.connect(self.db_path) as db:
            try:
                # First check if a similar task exists
                cursor = await db.execute("""
                    SELECT id FROM tasks 
                    WHERE title = ? AND description = ? AND due_date = ? AND created_by = ?
                """, (title, description, due_date, created_by))
                existing_task = await cursor.fetchone()
                
                if existing_task:
                    print(f"Task already exists with ID: {existing_task[0]}")  # Debug log
                    return existing_task[0]

                # If no existing task, insert new one
                cursor = await db.execute("""
                    INSERT INTO tasks (title, description, due_date, priority, status, created_by, assigned_to, created_at, updated_at)
                    VALUES (?, ?, ?, ?, 'pending', ?, ?, ?, ?)
                """, (title, description, due_date, priority, created_by, assigned_to, now, now))
                await db.commit()
                task_id = cursor.lastrowid
                print(f"Task added successfully with ID: {task_id}")  # Debug log
                return task_id
            except Exception as e:
                print(f"Error adding task: {e}")  # Debug log
                raise

    async def get_task(self, task_id):
        """Get a task by its ID."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM tasks WHERE id = ?
            """, (task_id,))
            return await cursor.fetchone()

    async def get_user_tasks(self, user_id, status=None):
        """Get all tasks for a user, optionally filtered by status."""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if status:
                cursor = await db.execute("""
                    SELECT * FROM tasks 
                    WHERE (created_by = ? OR assigned_to = ?)
                    AND status = ?
                    ORDER BY due_date ASC
                """, (user_id, user_id, status))
            else:
                cursor = await db.execute("""
                    SELECT * FROM tasks 
                    WHERE created_by = ? OR assigned_to = ?
                    ORDER BY due_date ASC
                """, (user_id, user_id))
            return await cursor.fetchall()

    async def update_task_status(self, task_id, status):
        """Update the status of a task."""
        now = datetime.now(pytz.UTC).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE tasks 
                SET status = ?, updated_at = ?
                WHERE id = ?
            """, (status, now, task_id))
            await db.commit()

    async def delete_task(self, task_id):
        """Delete a task by its ID."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            await db.commit()

    async def get_overdue_tasks(self):
        """Get all overdue tasks."""
        now = datetime.now(pytz.UTC).isoformat()
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM tasks 
                WHERE due_date < ? AND status != 'completed'
                ORDER BY due_date ASC
            """, (now,))
            return await cursor.fetchall() 