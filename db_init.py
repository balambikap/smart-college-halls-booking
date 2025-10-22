import sqlite3

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()

    # Drop tables if exist
    c.execute("DROP TABLE IF EXISTS users")
    c.execute("DROP TABLE IF EXISTS subjects")
    c.execute("DROP TABLE IF EXISTS halls")
    c.execute("DROP TABLE IF EXISTS bookings")

    # Users table
    c.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        is_admin INTEGER DEFAULT 0
    )''')

    # Subjects table
    c.execute('''CREATE TABLE subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )''')

    # Halls table
    c.execute('''CREATE TABLE halls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )''')

    # Bookings table
    c.execute('''CREATE TABLE bookings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        hall_id INTEGER NOT NULL,
        day TEXT NOT NULL,
        period TEXT NOT NULL,
        subject_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (hall_id) REFERENCES halls(id),
        FOREIGN KEY (subject_id) REFERENCES subjects(id)
    )''')

    # Insert admin user
    c.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)",
              ("admin", "admin123", 1))

    # Insert halls
    halls = [f"ICT Hall {i}" for i in range(1, 8)]
    c.executemany("INSERT INTO halls (name) VALUES (?)", [(h,) for h in halls])

    # Insert sample subjects
    subjects = [("Computer Science",), ("Zoology",), ("Chemistry",)]
    c.executemany("INSERT INTO subjects (name) VALUES (?)", subjects)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized with 7 halls, admin user, and sample departments.")
