import sqlite3
import requests
import os
import json

db_string = os.environ['DB_STRING']
acuity_userid = os.environ['ACUITY_USERID']
acuity_apikey = os.environ['ACUITY_APIKEY']
acuity_root = 'https://acuityscheduling.com/api/v1'

r = requests.get(acuity_root + '/calendars', auth=(acuity_userid, acuity_apikey))
calendars = r.json()

def to_query(calendar):
    return '''INSERT INTO salesperson (name) VALUES ('{}')'''.format(calendar['name'])

with sqlite3.connect(db_string) as connection:
    connection.execute('DELETE FROM salesperson')
    for calendar in calendars:
        connection.execute(to_query(calendar))

print('Synced with Acuity!')
