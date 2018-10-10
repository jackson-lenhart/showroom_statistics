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

class Salesperson(object):

    # index sends back all the salespeople
    @cherrypy.expose
    @cherrypy.tools.accept(media='text/plain')
    def index(self):
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

class Visitor(object):

    # TODO: index sends back all visitors currently waiting
    @cherrypy.expose
    def index(self):
        with sqlite3.connect(db_string) as connection:
            query = '''SELECT * FROM visitor WHERE is_waiting=1'''
            cursor = connection.execute(query)
            data = cursor.fetchall()

            # Comprehend list of tuples into json-friendly data
            return json.dumps([ jsonify_visitor(t) for t in data ])

    @cherrypy.expose
    def add(self):
        with sqlite3.connect(db_string) as connection:
            query = '''INSERT INTO visitor (name, is_waiting, has_visited_before) VALUES ('Isaac', 1, 0)'''
            connection.execute(query)
            return 'OK'

    # observe sets up an event stream with the client
    @cherrypy.expose
    def observe(self):
        def event_stream():
            with sqlite3.connect(db_string) as connection:
                query = '''SELECT * FROM visitor WHERE is_waiting=1'''
                cursor = connection.execute(query)
                visitors = cursor.fetchall()
                while True:
                    cursor = connection.execute(query)
                    latest_visitors = cursor.fetchall()
                    if len(latest_visitors) != len(visitors):
                        json_data = [ jsonify_visitor(t) for t in latest_visitors ]
                        yield 'data: ' + json.dumps(json_data) + '\n\n'
                        visitors = latest_visitors
        return event_stream()

    observe._cp_config = { 'response.stream': True }

# Takes a visitor tuple returned from SQL and turns it into a json-friendly dict
def jsonify_visitor(t):
    v = {
        'id': t[0],
        'name': t[1],
        'isWaiting': t[2],
        'hasVisitedBefore': t[3]
    }

    # Nullable fields
    if t[4]:
        v['salespersonId'] = t[4]
    if t[5]:
        v['notes'] = t[5]
    if t[6]:
        v['lookingFor'] = t[6]

    return v

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
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Access-Control-Allow-Origin', '*'), ('Content-Type', 'text/plain')]
        },
        '/visitor': {
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Access-Control-Allow-Origin', '*'), ('Content-Type', 'text/event-stream')]
        }
    }
    app = Main()
    app.salesperson = Salesperson()
    app.visitor = Visitor()
    cherrypy.quickstart(app, '/api', conf)
