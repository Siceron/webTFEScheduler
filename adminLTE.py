import web
import sys
import math
from models import *
from json_utils import *
from parser_utils import *
from export_utils import *
from conflicts_report import *
from subprocess import Popen, PIPE, STDOUT
import json
from pprint import pprint
import datetime
import hashlib
from datetime import datetime

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
    '/get_commission', 'get_commission',
    '/set_session', 'set_session',
    '/set_tfe', 'set_tfe',
    '/delete_tfe', 'delete_tfe',
    '/set_student', 'set_student',
    '/delete_student', 'delete_student',
    '/set_person', 'set_person',
    '/delete_person', 'delete_person',
    '/get_tfe_rel_student', 'get_tfe_rel_student',
    '/set_tfe_rel_student', 'set_tfe_rel_student',
    '/set_tfe_rel_person', 'set_tfe_rel_person',
    '/delete_tfe_rel_person', 'delete_tfe_rel_person',
    '/is_up_to_date', 'is_up_to_date',
    '/get_conflicts', 'get_conflicts',
    '/parametrization', 'parametrization',
    '/csv_export', 'csv_export',
    '/excel_export', 'excel_export'
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
            session.log = datetime.now()
            raise web.seeother('/index')   
        else:
            return "Those login details don't work."

class index:

    def GET(self):
        if session.get('username', False):
            tfe_nbr = Tfe.select().count()
            rooms = math.ceil(tfe_nbr/(3*12))
            parametrization = Parametrization.select().count()
            return render.index(rooms, parametrization)
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
            if Parametrization.select().count() > 0:
                tfes = Tfe.select()
                session.log = datetime.now()
                parametrization = Parametrization.select()[0]
                return render.scheduler(tfes, parametrization)
            else:
                raise web.seeother('/index')
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
            tfes = Tfe.select()
            students = Student.select()
            return render.student(students, tfes)
        else:
           raise web.seeother('/')

class person:
    def GET(self):
        if session.get('username', False):
            tfes = Tfe.select()
            persons = Person.select()
            rels = Tfe_rel_person.select()
            return render.person(persons, rels, tfes)
        else:
           raise web.seeother('/')

class logout:
    def GET(self):
        session.kill()
        raise web.seeother('/')

def set_commission(data_commission, commission):
    for i in data_commission[commission]:
        tfe = Tfe.select(Tfe.q.code == i)[0]
        if tfe.commission == "TBD":
            tfe.commission = commission

class executescheduler:
    def POST(self):
        x = web.input()
        with open("input.JSON", "w") as outfile:
            json.dump(create_input_json(), outfile, indent=4)
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

        with open('commissions.JSON') as data_file_commission:    
            data_commission = json.load(data_file_commission)

        set_commission(data_commission, "ELEC")
        set_commission(data_commission, "ELME")
        set_commission(data_commission, "GBIO")
        set_commission(data_commission, "FYAP")
        set_commission(data_commission, "KIMA")
        set_commission(data_commission, "GCE")
        set_commission(data_commission, "INFO")
        set_commission(data_commission, "SINF")
        set_commission(data_commission, "MAP")
        set_commission(data_commission, "MECA")

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
            "readers" : readers,
            "moderator": tfe.moderator
        }
        return json.dumps(result)

class get_commission:
    def POST(self):
        x = web.input()
        tfe = Tfe.select(Tfe.q.code==x.code)[0]
        if tfe.commission == None:
            return ""
        else:
            return tfe.commission

class set_session:
    def POST(self):
        x = web.input()
        tfe = Tfe.select(Tfe.q.code == x.code)[0]
        tfe.session = int(x.session)
        tfe.log = datetime.now()
        session.log = datetime.now()
        return "ok"

class set_tfe:
    def POST(self):
        x = web.input()
        if x.code.strip() != "" and x.title.strip() != "":
            if Tfe.select(Tfe.q.code == x.code).count() == 0:
                Tfe(code=x.code, title=x.title, commission=x.commission, moderator=x.moderator)
            else:
                tfe = Tfe.select(Tfe.q.code == x.code)[0]
                tfe.title = x.title
                tfe.commission = x.commission
                tfe.moderator = x.moderator
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
        if x.email.strip() != "" and x.lastname.strip() != "" and x.firstname.strip() != "" and x.faculty.strip() != "":
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
        if x.email.strip() != "" and x.firstname.strip() != "" and x.lastname.strip() != "":
            if Person.select(Person.q.email == x.email).count() == 0:
                disponibility = Disponibility(session_0=isChecked(x, 's0'), session_1=isChecked(x, 's1'), session_2=isChecked(x, 's2'), session_3=isChecked(x, 's3'),\
                session_4=isChecked(x, 's4'), session_5=isChecked(x, 's5'), session_6=isChecked(x, 's6'), session_7=isChecked(x, 's7'), session_8=isChecked(x, 's8'),\
                session_9=isChecked(x, 's9'), session_10=isChecked(x, 's10'), session_11=isChecked(x, 's11'))
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

class get_tfe_rel_student:
    def POST(self):
        x = web.input()
        student = Student.select(Student.q.email == x.email)[0]
        if Tfe_rel_student.select(Tfe_rel_student.q.student == student).count() == 0:
            return ""
        else:
            rel = Tfe_rel_student.select(Tfe_rel_student.q.student == student)[0]
            return rel.tfe.code

class set_tfe_rel_student:
    def POST(self):
        x = web.input()
        student = Student.select(Student.q.email == x.email)[0]
        if x.tfe == "":
            if Tfe_rel_student.select(Tfe_rel_student.q.student == student).count() != 0:
                rel = Tfe_rel_student.select(Tfe_rel_student.q.student == student)[0]
                rel.delete(rel.id)
        else:
            tfe = Tfe.select(Tfe.q.code == x.tfe)[0]
            Tfe_rel_student(tfe=tfe, student=student)
        raise web.seeother('/student')

class set_tfe_rel_person:
    def POST(self):
        x = web.input()
        if Person.select(Person.q.email == x.person).count() != 0 and Tfe.select(Tfe.q.code == x.tfe).count() != 0:
            person = Person.select(Person.q.email == x.person)[0]
            tfe = Tfe.select(Tfe.q.code == x.tfe)[0]
            if Tfe_rel_person.select(AND(Tfe_rel_person.q.person == person, Tfe_rel_person.q.tfe == tfe)).count() == 0:
                Tfe_rel_person(tfe=tfe, person=person, title=x.title)
        raise web.seeother('/person')

class delete_tfe_rel_person:
    def POST(self):
        x = web.input()
        person = Person.select(Person.q.email == x.person)[0]
        tfe = Tfe.select(Tfe.q.code == x.tfe)[0]
        rel = Tfe_rel_person.select(AND(Tfe_rel_person.q.person == person, Tfe_rel_person.q.tfe == tfe))[0]
        rel.delete(rel.id)
        return "ok"

class is_up_to_date:
    def POST(self):
        x = web.input()
        tfe = Tfe.select(Tfe.q.code == x.code)[0]
        if tfe.log < session.log:
            return "True"
        else:
            return "False"

class get_conflicts:
    def POST(self):
        x = web.input()
        result = get_conflicts_json(x.code, x.session)
        return result

class parametrization:
    def POST(self):
        x = web.input()
        day1 = datetime.strptime(x.day1, '%d/%m/%Y')
        day2 = datetime.strptime(x.day2, '%d/%m/%Y')
        day3 = datetime.strptime(x.day3, '%d/%m/%Y')
        Parametrization(rooms_number=int(x.rooms), day_1=day1, day_2=day2, day_3=day3, reserve=int(x.reserve)-1)
        return "ok"

class csv_export:
    def GET(self):
        export_data("static/")
        return "ok"

class excel_export:
    def GET(self):
        export_data_excel("static/")
        return "ok"

if __name__ == "__main__":
    app = web.application(urls, globals())
    db = web.database(dbn='sqlite', db='tfescheduler.db')
    store = web.session.DBStore(db, 'sessions')
    session = web.session.Session(app, store, initializer={'count': 0})
    app.add_processor(load_sqlo)
    app.run()