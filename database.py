import sqlite3

def create_database():
    conn = sqlite3.connect("edonation.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            mobile TEXT NOT NULL,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT,
            mobile TEXT,
            item TEXT NOT NULL,
            category TEXT,
            item_condition TEXT,
            location TEXT NOT NULL,
            description TEXT
        )
    """)

    try:
        cursor.execute(
            "ALTER TABLE donations ADD COLUMN status TEXT DEFAULT 'Pending'"
        )
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_database()
    print("Database updated successfully!")