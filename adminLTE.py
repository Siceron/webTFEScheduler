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
    '/tfe', 'tfe',
    '/student', 'student',
    '/person', 'person',
    '/executescheduler', 'executescheduler',
    '/show_tfe_details', 'show_tfe_details',
    '/set_session', 'set_session',
    '/set_tfe', 'set_tfe',
    '/delete_tfe', 'delete_tfe',
    '/set_student', 'set_student',
    '/delete_student', 'delete_student',
    '/set_person', 'set_person',
    '/delete_person', 'delete_person'
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
        check = User.select(AND(User.q.email==i.username, User.q.password == pwdhash)).count()
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
            return render.index(rooms)
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

class tfe:
    def GET(self):
        if session.get('username', False):
            tfes = Tfe.select()
            return render.tfe(tfes)
        else:
           raise web.seeother('/')

class student:
    def GET(self):
        if session.get('username', False):
            students = Student.select()
            return render.student(students)
        else:
           raise web.seeother('/')

class person:
    def GET(self):
        if session.get('username', False):
            persons = Person.select()
            return render.person(persons)
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

        advisors_data = Tfe_rel_person.select(AND(Tfe_rel_person.q.tfe==tfe, Tfe_rel_person.q.title=="Promoteur"))
        advisors = []
        for rel in advisors_data:
            advisors.append(rel.person.email)

        readers_data = Tfe_rel_person.select(AND(Tfe_rel_person.q.tfe==tfe, Tfe_rel_person.q.title=="Lecteur"))
        readers = []
        for rel in readers_data:
            readers.append(rel.person.email)

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

class set_tfe:
    def POST(self):
        x = web.input()
        if Tfe.select(Tfe.q.code == x.code).count() == 0:
            Tfe(code=x.code, title=x.title, commission=x.commission)
        else:
            tfe = Tfe.select(Tfe.q.code == x.code)[0]
            tfe.title = x.title
            tfe.commission = x.commission
        raise web.seeother('/tfe')

class delete_tfe:
    def POST(self):
        x = web.input()
        tfe = Tfe.select(Tfe.q.code == x.code)[0]
        tfe.delete(tfe.id)
        return "ok"

class set_student:
    def POST(self):
        x = web.input()
        if Student.select(Student.q.email == x.email).count() == 0:
            Student(email=x.email, name=x.firstname, last_name=x.lastname, faculty=x.faculty)
        else:
            student = Student.select(Student.q.email == x.email)[0]
            student.name = x.firstname
            student.last_name = x.lastname
            student.faculty = x.faculty
        raise web.seeother('/student')

class delete_student:
    def POST(self):
        x = web.input()
        student = Student.select(Student.q.email == x.email)[0]
        tfe_relations = []
        for rel in Tfe_rel_student.select(Tfe_rel_student.q.student == student):
            tfe_relations.append(rel)
        student.delete(student.id)
        for rel in tfe_relations:
            rel.delete(rel.id)
        return "ok"

def isChecked(input, param):
    if param in input:
        return True
    else:
        return False

class set_person:
    def POST(self):
        x = web.input()
        if Person.select(Person.q.email == x.email).count() == 0:
            disponibility = Disponibility(session_0=x.s0, session_1=x.s1, session_2=x.s2, session_3=x.s3,\
            session_4=x.s4, session_5=x.s5, session_6=x.s6, session_7=x.s7, session_8=x.s8,\
            session_9=x.s9, session_10=x.s10, session_11=x.s11)
            Person(email=x.email, name=x.firstname, last_name=x.lastname, disponibility=disponibility)
        else:
            person = Person.select(Person.q.email == x.email)[0]
            person.name = x.firstname
            person.last_name = x.lastname
            person.disponibility.session_0 = isChecked(x, 's0')
            person.disponibility.session_1 = isChecked(x, 's1')
            person.disponibility.session_2 = isChecked(x, 's2')
            person.disponibility.session_3 = isChecked(x, 's3')
            person.disponibility.session_4 = isChecked(x, 's4')
            person.disponibility.session_5 = isChecked(x, 's5')
            person.disponibility.session_6 = isChecked(x, 's6')
            person.disponibility.session_7 = isChecked(x, 's7')
            person.disponibility.session_8 = isChecked(x, 's8')
            person.disponibility.session_9 = isChecked(x, 's9')
            person.disponibility.session_10 = isChecked(x, 's10')
            person.disponibility.session_11 = isChecked(x, 's11')
        raise web.seeother('/person')

class delete_person:
    def POST(self):
        x = web.input()
        person = Person.select(Person.q.email == x.email)[0]
        disponibility = person.disponibility
        tfe_relations = []
        for rel in Tfe_rel_person.select(Tfe_rel_person.q.person == person):
            tfe_relations.append(rel)
        person.delete(person.id)
        disponibility.delete(disponibility.id)
        for rel in tfe_relations:
            rel.delete(rel.id)
        return "ok"

if __name__ == "__main__":
    app = web.application(urls, globals())
    db = web.database(dbn='sqlite', db='tfescheduler.db')
    store = web.session.DBStore(db, 'sessions')
    session = web.session.Session(app, store, initializer={'count': 0})
    app.add_processor(load_sqlo)
    app.run()