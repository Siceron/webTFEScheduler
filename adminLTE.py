import web
import sys
import math
from models import *
from json_utils import *
from parser_utils import *
from subprocess import Popen, PIPE, STDOUT
import json
from pprint import pprint
import hashlib

web.config.debug = False
web.config.session_parameters['cookie_name'] = 'tfescheduler_session_id'

render = web.template.render('templates/')

urls = (
    '/', 'login',
    '/logout', 'logout',
    '/index', 'index',
    '/scheduler', 'scheduler',
    '/informations', 'informations',
    '/executescheduler', 'executescheduler',
    '/show_tfe_details', 'show_tfe_details',
    '/set_session', 'set_session'
)

def load_sqlo(handler=None):
    con = connectionForURI('sqlite:tfescheduler.db')
    if not web.ctx.has_key('env'):  # not using web.py
        sqlhub.processConnection = con
        return
    trans = con.transaction()
    sqlhub.threadConnection = trans
    try:
        return handler()
    except web.HTTPError:
        trans.commit(close=True)
        raise
    except:
        trans.rollback()
        trans.begin()
        raise
    finally:
        trans.commit(close=True)

class login:

    def GET(self):
        if session.get('username', False):
            raise web.seeother('/index')
        else:
            return render.login()

    def POST(self):
        i = web.input()

        #authdb = sqlite3.connect('users.db')
        pwdhash = hashlib.md5(i.password.encode('utf-8')).hexdigest()
        check = User.select(AND(User.q.user==i.username, User.q.password == pwdhash)).count()
        #check = authdb.execute('select * from users where username=? and password=?', (i.username, pwdhash))
        if check == 1: 
            session.loggedin = True
            session.username = i.username
            raise web.seeother('/index')   
        else:
            return "Those login details don't work."

class index:

    def GET(self):
        if session.get('username', False):
            tfe_nbr = Tfe.select().count()
            rooms = math.ceil(tfe_nbr/(3*12))
            return render.starter(rooms)
        else:
           raise web.seeother('/')

    def POST(self):
        """ Store csv file """
        x = web.input(myfile={})
        populate_db(x)
        raise web.seeother('/index')

class scheduler:
    def GET(self):
        if session.get('username', False):
            tfes = Tfe.select()
            return render.scheduler(tfes)
        else:
           raise web.seeother('/')

class informations:
    def GET(self):
        if session.get('username', False):
            students = Student.select()
            advisors = Advisor.select()
            tfes = Tfe.select()
            readers = Reader.select()
            return render.informations(students, advisors, tfes, readers)
        else:
           raise web.seeother('/')

class logout:
    def GET(self):
        session.kill()
        raise web.seeother('/')

class executescheduler:
    def POST(self):
        x = web.input()
        with open("input.JSON", "w") as outfile:
            json.dump(create_input_json(x.rooms), outfile, indent=4)
        proc = Popen(["java", "-jar", "scheduler/TFEScheduler.jar", "input.JSON", x.time], stdout=PIPE, stderr=STDOUT)
        proc.wait()
        print("hello")
        for line in proc.stdout:
            print(line)

        with open('output.JSON') as data_file:    
            data = json.load(data_file)

        for i in data:
            tfe = Tfe.select(Tfe.q.code == i["code"])[0]
            tfe.session=i["session"]

        return "ok"

class show_tfe_details:
    def POST(self):
        x = web.input()
        tfe = Tfe.select(Tfe.q.code==x.code)[0]

        students_data = Tfe_rel_student.select(Tfe_rel_student.q.tfe==tfe)
        students = []
        for rel in students_data:
            students.append(rel.student.email)

        advisors_data = Tfe_rel_advisor.select(Tfe_rel_advisor.q.tfe==tfe)
        advisors = []
        for rel in advisors_data:
            advisors.append(rel.advisor.email)

        readers_data = Tfe_rel_reader.select(Tfe_rel_reader.q.tfe==tfe)
        readers = []
        for rel in readers_data:
            readers.append(rel.reader.email)

        result = {
            "title" : tfe.title,
            "students" : students,
            "advisors" : advisors,
            "readers" : readers
        }
        return json.dumps(result)

class set_session:
    def POST(self):
        x = web.input()
        tfe = Tfe.select(Tfe.q.code == x.code)[0]
        tfe.session = int(x.session)
        return "ok"

if __name__ == "__main__":
    app = web.application(urls, globals())
    db = web.database(dbn='sqlite', db='tfescheduler.db')
    store = web.session.DBStore(db, 'sessions')
    session = web.session.Session(app, store, initializer={'count': 0})
    app.add_processor(load_sqlo)
    app.run()