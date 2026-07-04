import aiosqlite
from config import DB_NAME

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                joined_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.execute('''
            CREATE TABLE IF NOT EXISTS invitations (
                user_id INTEGER PRIMARY KEY,
                event_type TEXT,
                title TEXT,
                host TEXT,
                date_str TEXT,
                time_str TEXT,
                venue TEXT,
                rsvp TEXT,
                template TEXT DEFAULT 'Elegant'
            )
        ''')
        await db.commit()

async def register_user(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        await db.commit()

async def save_invitation(user_id: int, data: dict):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            INSERT OR REPLACE INTO invitations (user_id, event_type, title, host, date_str, time_str, venue, rsvp, template)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, data.get('event_type'), data.get('title'), data.get('host'),
              data.get('date_str'), data.get('time_str'), data.get('venue'), data.get('rsvp'), data.get('template', 'Elegant')))
        await db.commit()

async def get_invitation(user_id: int):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT event_type, title, host, date_str, time_str, venue, rsvp, template FROM invitations WHERE user_id = ?", (user_id,)) as cursor:
            row = await cursor.fetchone()
            if row:
                return {
                    "event_type": row[0], "title": row[1], "host": row[2],
                    "date_str": row[3], "time_str": row[4], "venue": row[5],
                    "rsvp": row[6], "template": row[7]
                }
            return None

async def get_analytics():
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM users") as c1, db.execute("SELECT COUNT(*) FROM invitations") as c2:
            u_count = (await c1.fetchone())[0]
            i_count = (await c2.fetchone())[0]
            return u_count, i_count

