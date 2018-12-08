import mysql.connector
import os

server_password = os.environ['SERVER_PASSWORD']

config = {
  'host':'showroom-statistics1.mysql.database.azure.com',
  'user': 'jackson-lenhart@showroom-statistics1',
  'password': server_password,
  'database': 'showroom_statistics'
}

conn = mysql.connector.connect(**config)
cursor = conn.cursor()

query = '''INSERT INTO salesperson (name, is_active, department)
    VALUES ('Jason Anemaet', b'1', 'Appliance'),
    ('Rick Medeiros', b'1', 'Appliance'),
    ('Paul Gillis', b'1', 'Appliance'),
    ('Adam Thomashow', b'1', 'Appliance'),
    ('Kathy Alves', b'1', 'Appliance'),
    ('Frank Pasini', b'1', 'Appliance'),
    ('Rhonda Niddrie', b'1', 'Appliance'),
    ('Amy Zuckerman', b'1', 'Lighting'),
    ('Chris Wurlitzer', b'0', 'Appliance'),
    ('Jesse Long', b'0', 'Appliance'),
    ('John Ramsay', b'0', 'Appliance')'''

cursor.execute('DELETE FROM salesperson')
cursor.execute(query);
conn.commit()
cursor.close()
conn.close()

print('OK')
