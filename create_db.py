import sqlite3


conn = sqlite3.connect('diet.db')


cursor = conn.cursor()


create_table_query = '''
CREATE TABLE IF NOT EXISTS food (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    category TEXT NOT NULL,
    calorie INTEGER NOT NULL,
    date_of_reception TEXT NOT NULL
);
'''
create_user_query = ('''
    CREATE TABLE IF NOT EXISTS user (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        last_login DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute(create_table_query)
cursor.execute(create_user_query)

conn.commit()
conn.close()
