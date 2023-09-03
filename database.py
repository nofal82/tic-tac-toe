import sqlite3

def create_database():
    db_connection = sqlite3.connect('game_database.db')
    cursor = db_connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            confirmed INTEGER DEFAULT 0
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            token TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    # Create the gameplay_data table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gameplay_data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        winner TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    db_connection.commit()
    cursor.close()
    db_connection.close()