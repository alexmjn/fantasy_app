import sqlite3

def create_tables():
    conn = sqlite3.connect('fantasy.db')

    conn.execute('''
        CREATE TABLE players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
    ''')

    conn.execute('''
        CREATE TABLE objects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            player_id INTEGER,
            FOREIGN KEY (player_id) REFERENCES players(id)
        );
            ''')

    conn.execute('''
        CREATE TABLE categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            points INTEGER NOT NULL
        );
            ''')

    conn.execute('''
        CREATE TABLE points (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            object_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            week INTEGER NOT NULL,
            FOREIGN KEY (object_id) REFERENCES objects(id),
            FOREIGN KEY (category_id) REFERENCES categories(id)
        );
    ''')


    conn.commit()
    conn.close()

if __name__ == '__main__':
    create_tables()
