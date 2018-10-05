import sqlite3
import os

db_string = os.environ['DB_STRING']

sql_commands = [
    '''DROP TABLE IF EXISTS visitor''',
    # '''DROP TABLE IF EXISTS salesperson''',
    '''CREATE TABLE IF NOT EXISTS visitor (
        id INTEGER PRIMARY KEY,
        name varchar(255) NOT NULL,
        is_waiting bit NOT NULL,
        has_visited_before bit NOT NULL,
        salesperson_id REFERENCES salesperson(id),
        notes varchar(255),
        looking_for varchar(255)
    )''',
    '''CREATE TABLE IF NOT EXISTS salesperson (
        id INTEGER PRIMARY KEY,
        name varchar(255) NOT NULL,
        department varchar(255)
    )'''
]

with sqlite3.connect(db_string) as connection:
    for command in sql_commands:
        connection.execute(command)

print('Tables created!')
