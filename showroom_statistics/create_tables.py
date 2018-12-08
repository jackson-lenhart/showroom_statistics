import mysql.connector
import os

server_password = os.environ['SERVER_PASSWORD']

config = {
  'host':'showroom-statistics1.mysql.database.azure.com',
  'user': 'jackson-lenhart@showroom-statistics1',
  'password': server_password,
  'database': 'showroom_statistics'
}

sql_commands = [
    '''DROP TABLE IF EXISTS salesperson''',
    '''DROP TABLE IF EXISTS statistics''',
    '''CREATE TABLE IF NOT EXISTS salesperson (
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        is_active BIT(1) NOT NULL,
        department ENUM('Appliance', 'Lighting')
    )''',
    '''CREATE TABLE IF NOT EXISTS statistics (
        id INTEGER AUTO_INCREMENT PRIMARY KEY,
        signed_in_timestamp INTEGER NOT NULL,
        wait_time INTEGER NOT NULL,
        visitor_id INTEGER REFERENCES visitor(id),
        salesperson_id INTEGER REFERENCES salesperson(id),
        salesperson_who_helped_id INTEGER REFERENCES salesperson(id),
        looking_for VARCHAR(255),
        department ENUM('Appliance', 'Lighting')
    )''',
]

conn = mysql.connector.connect(**config)
cursor = conn.cursor()
for command in sql_commands:
    cursor.execute(command)

print('Tables created!')
