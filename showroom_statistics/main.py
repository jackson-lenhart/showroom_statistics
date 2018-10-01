import cherrypy
import sqlite3
import json
import datetime
import requests
import os

db_string = os.environ['DB_STRING']
acuity_userid = os.environ['ACUITY_USERID']
acuity_apikey = os.environ['ACUITY_APIKEY']

acuity_root = 'https://acuityscheduling.com/api/v1'

today = datetime.datetime.today().strftime('%Y-%m-%d')
print(today)

SQL = 'INSERT INTO stuff VALUES (4)'

class Main(object):
    @cherrypy.expose
    def index(self):
        with sqlite3.connect(db_string) as connection:
            connection.execute(SQL)
        return 'OK'
    # This will get current calendars on acuity
    @cherrypy.expose
    def calendars(self):
        r = requests.get(acuity_root + '/calendars', auth=(acuity_userid, acuity_apikey))
        calendars = r.json()
        return json.dumps(calendars)
    # This will get today's appointments
    @cherrypy.expose
    def appointments(self):
        today = datetime.datetime.today().strftime('%Y-%m-%d')
        payload = {
            'minDate': today,
            'maxDate': today
        }
        r = requests.get(acuity_root + '/appointments', params=payload, auth=(acuity_userid, acuity_apikey))
        appts = r.json()
        return json.dumps(appts)

if __name__ == '__main__':
    cherrypy.config.update({
        'server.socket_port': 9090,
    })
    conf = {
        '/': {
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Access-Control-Allow-Origin', '*')]
        }
    }
    cherrypy.quickstart(Main(), '/', conf)
