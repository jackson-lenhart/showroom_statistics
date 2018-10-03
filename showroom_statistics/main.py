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

@cherrypy.expose
class Salesperson(object):

    # GET sends back all the salespeople
    @cherrypy.tools.accept(media='text/plain')
    def GET(self):
        query = '''SELECT * FROM salesperson'''
        with sqlite3.connect(db_string) as connection:
            cursor = connection.execute(query)
            sql_data = cursor.fetchall()
            json_data = []
            for t in sql_data:
                sp = {
                    'id': t[0],
                    'name': t[1]
                }
                if t[2]:
                    sp['department']: t[2]
                json_data.append(sp)
            return json.dumps(json_data)

if __name__ == '__main__':
    cherrypy.config.update({
        'server.socket_port': 9090,
    })
    conf = {
        '/': {
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Access-Control-Allow-Origin', '*')]
        },
        '/salesperson': {
            'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Access-Control-Allow-Origin', '*'), ('Content-Type', 'text/plain')]
        }
    }
    app = Main()
    app.salesperson = Salesperson()
    cherrypy.quickstart(app, '/api', conf)
