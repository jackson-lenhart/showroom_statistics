import cherrypy
import mysql.connector
import json
import datetime
import requests
import os
import time

acuity_userid = os.environ['ACUITY_USERID']
acuity_apikey = os.environ['ACUITY_APIKEY']

acuity_root = 'https://acuityscheduling.com/api/v1'

today = datetime.datetime.today().strftime('%Y-%m-%d')

server_password = os.environ['SERVER_PASSWORD']

config = {
  'host':'showroom-statistics1.mysql.database.azure.com',
  'user': 'jackson-lenhart@showroom-statistics1',
  'password': server_password,
  'database': 'showroom_statistics'
}

conn = mysql.connector.connect(**config)
cursor = conn.cursor()

QUEUE = []
INCREMENTING_ID = 1

class Main(object):
    @cherrypy.expose
    def index(self):
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

        # selecting only active because this will be for list management
        # not statistics/reports
        query = 'SELECT * FROM salesperson WHERE is_active=1'
        cursor.execute(query)
        sql_data = cursor.fetchall()
        json_data = []
        for t in sql_data:
            sp = {
                'id': t[0],
                'name': t[1]
            }
            if t[3]:
                sp['department']: t[3]
            json_data.append(sp)
        return json.dumps(json_data)

def hash_queue(q):
    list_of_hashes = [hash(frozenset(d.items())) for d in q]
    return hash(tuple(list_of_hashes))

class Visitor(object):

    # index sends back all visitors currently waiting
    @cherrypy.expose
    def index(self):
        global QUEUE

        return json.dumps(QUEUE)

    # accepts a json 'visitor' object
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def add(self):
        global INCREMENTING_ID
        global QUEUE

        req_data = cherrypy.request.json
        visitor = {
            'name': req_data['name'],
            'is_waiting': req_data['isWaiting'],
            'has_visited_before': req_data['hasVisitedBefore'],
            'signed_in_timestamp': req_data['signedInTimestamp']
        }

        # nullable fields
        nullable = ['salespersonId', 'notes', 'lookingFor']
        for k in nullable:
            if k in req_data:
                visitor[k] = req_data[k]
            else:
                visitor[k] = None

        visitor['id'] = INCREMENTING_ID
        INCREMENTING_ID += 1

        QUEUE.append(visitor)

    # sets up an event stream with the client
    @cherrypy.expose
    def observe(self):
        def event_stream():
            global QUEUE
            qhash = hash_queue(QUEUE)
            while True:
                curr_qhash = hash_queue(QUEUE)
                if curr_qhash != qhash:
                    qhash = curr_qhash
                    yield 'data: ' + json.dumps(QUEUE) + '\n\n'
                    time.sleep(1)
        return event_stream()

    observe._cp_config = { 'response.stream': True }

class Statistics(object):

    # inserts all data relevant to a customer being helped
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def helped(self):
        global QUEUE
        global INCREMENTING_ID

        up_data = cherrypy.request.json
        print(up_data)
        customer = up_data['customer']
        for v in QUEUE:
            if v['id'] == customer['id']:
                QUEUE.remove(v)
                INCREMENTING_ID += 1

                # TODO: visited_before field
                query = '''INSERT INTO statistics (
                    signed_in_timestamp,
                    wait_time,
                    visitor_id,
                    salesperson_id,
                    salesperson_who_helped_id,
                    looking_for,
                    department
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)'''
                values = (
                    customer['signed_in_timestamp'],
                    int(time.time()) - customer['signed_in_timestamp'],
                    customer['id'],
                    customer['salespersonId'],
                    up_data['salespersonId'],
                    customer['lookingFor'],
                    # hard coding this for now because implementing department
                    # on front-end form is TODO
                    'Appliance'
                )
                cursor.execute(query, values)
                conn.commit()
                return 'OK'

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
        },
        '/statistics': {
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Access-Control-Allow-Origin', '*'), ('Content-Type', 'text/event-stream')]
        }
    }

    app = Main()
    app.salesperson = Salesperson()
    app.visitor = Visitor()
    app.statistics = Statistics()
    cherrypy.quickstart(app, '/api', conf)
