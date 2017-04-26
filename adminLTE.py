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
    '/auditoriums', 'auditoriums',
    '/executescheduler', 'executescheduler',
    '/show_tfe_details', 'show_tfe_details',
    '/set_prevented', 'set_prevented',
    '/get_commission', 'get_commission',
    '/set_session', 'set_session',
    '/set_tfe', 'set_tfe',
    '/delete_tfe', 'delete_tfe',
    '/set_student', 'set_student',
    '/delete_student', 'delete_student',
    '/set_person', 'set_person',
    '/delete_person', 'delete_person',
    '/set_auditorium', 'set_auditorium',
    '/get_tfe_rel_student', 'get_tfe_rel_student',
    '/set_tfe_rel_student', 'set_tfe_rel_student',
    '/set_tfe_rel_person', 'set_tfe_rel_person',
    '/delete_tfe_rel_person', 'delete_tfe_rel_person',
    '/is_up_to_date', 'is_up_to_date',
    '/get_conflicts', 'get_conflicts',
    '/parametrization', 'parametrization',
    '/csv_export', 'csv_export',
    '/excel_export', 'excel_export',
    '/set_conflict', 'set_conflict',
    '/set_user', 'set_user',
    '/reset_db', 'reset_db'
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
        pwdhash = hashlib.md5(i.password.encode('utf-8')).hexdigest()
        check = User.select(AND(User.q.email==i.username, User.q.password == pwdhash)).count()
        if check == 1: 
            session.loggedin = True
            session.username = i.username
            session.log = datetime.now()
            raise web.seeother('/index')   
        else:
            return render.message("Ces logins sont erronés")

class index:

    def GET(self):
        if session.get('username', False):
            user = User.select(User.q.email == session.get('username', False))[0]
            if(user.permission == 1):
                tfe_nbr = Tfe.select().count()
                rooms = math.ceil(tfe_nbr/(3*12))
                parametrization = Parametrization.select().count()
                username = session.get('username', False)
                return render.index_admin(rooms, parametrization, username)
            else:
                username = session.get('username', False)
                return render.index(username)
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
                auditoriums = Room.select()
                username = session.get('username', False)
                return render.scheduler(tfes, parametrization, auditoriums, username)
            else:
                return render.message("Veuillez attendre qu'un admin entre la parametrisation")
        else:
           raise web.seeother('/')

class tfe:
    def GET(self):
        if session.get('username', False):
            tfes = tfes_full_json()
            username = session.get('username', False)
            return render.tfe(tfes, username)
        else:
           raise web.seeother('/')

class student:
    def GET(self):
        if session.get('username', False):
            tfes = Tfe.select(orderBy="code")
            students = Student.select()
            username = session.get('username', False)
            return render.student(students, tfes, username)
        else:
           raise web.seeother('/')

class person:
    def GET(self):
        if session.get('username', False):
            tfes = Tfe.select(orderBy="code")
            persons = Person.select()
            rels = Tfe_rel_person.select()
            username = session.get('username', False)
            if Parametrization.select().count() == 0:
                parametrization = 0
                return render.person(persons, rels, tfes, parametrization, username)
            else:
                parametrization = Parametrization.select()[0]
                return render.person(persons, rels, tfes, parametrization, username)
        else:
           raise web.seeother('/')

class auditoriums:
    def GET(self):
        if session.get('username', False):
            auditoriums = Room.select()
            username = session.get('username', False)
            return render.auditoriums(auditoriums, username)
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
        set_commission(data_commission, "NANO")
        set_commission(data_commission, "GCE")
        set_commission(data_commission, "INFO")
        set_commission(data_commission, "SINF")
        set_commission(data_commission, "MAP")
        set_commission(data_commission, "MECA")

        return "ok"

def is_in_conflicts(email, conflicts, sessionNbr):
    result = False
    if int(sessionNbr) == -1:
        return False
    for i in conflicts['not_disponible']:
        if email == i['email']:
            result = True
            break
    if result == False:
        for i in conflicts['parallel']:
            if email == i['email']:
                result = True
                break
    return result

class show_tfe_details:
    def POST(self):
        x = web.input()
        tfe = Tfe.select(Tfe.q.code==x.code)[0]

        conflicts = get_conflicts_json(x.code, x.session)

        students_data = Tfe_rel_student.select(Tfe_rel_student.q.tfe==tfe)
        students = []
        for rel in students_data:
            students.append(rel.student.email)

        advisors_data = Tfe_rel_person.select(AND(Tfe_rel_person.q.tfe==tfe, Tfe_rel_person.q.title=="Promoteur"))
        advisors = []
        for rel in advisors_data:
            advisor = {
                "email" : rel.person.email,
                "prevented" : rel.prevented,
                "readonly" : is_in_conflicts(rel.person.email, conflicts, x.session)
            }
            advisors.append(advisor)

        readers_data = Tfe_rel_person.select(AND(Tfe_rel_person.q.tfe==tfe, Tfe_rel_person.q.title=="Lecteur"))
        readers = []
        for rel in readers_data:
            reader = {
                "email" : rel.person.email,
                "prevented" : rel.prevented,
                "readonly" : is_in_conflicts(rel.person.email, conflicts, x.session)
            }
            readers.append(reader)

        result = {
            "code" : tfe.code,
            "title" : tfe.title,
            "students" : students,
            "advisors" : advisors,
            "readers" : readers,
            "moderator": tfe.moderator
        }
        return json.dumps(result)

class set_prevented:
    def POST(self):
        x = web.input()
        tfe = Tfe.select(Tfe.q.code==x.code)[0]
        person = Person.select(Person.q.email==x.email)[0]
        rel = Tfe_rel_person.select(AND(Tfe_rel_person.q.tfe==tfe, Tfe_rel_person.q.person==person))[0]
        if x.check == "true":
            rel.prevented = True
        else:
            rel.prevented = False
        return "ok"

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
        return "ok"

class set_tfe:
    def POST(self):
        x = web.input()
        if x.code.strip() != "" and x.title.strip() != "":
            if Tfe.select(Tfe.q.code == x.code).count() == 0:
                Tfe(code=x.code, title=x.title, commission=x.commission, moderator=x.moderator, \
                    confidential=isChecked(x, 'confidential'), cpme=isChecked(x, 'cpme'), open_hub=isChecked(x, 'openhub'))
            else:
                tfe = Tfe.select(Tfe.q.code == x.code)[0]
                tfe.title = x.title
                tfe.commission = x.commission
                tfe.moderator = x.moderator
                tfe.confidential = isChecked(x, 'confidential')
                tfe.cpme = isChecked(x, 'cpme')
                tfe.open_hub = isChecked(x, 'openhub')
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

class set_auditorium:
    def POST(self):
        x = web.input()
        if x.name.strip() != "":
            auditorium = Room.select(Room.q.id == x.id)[0]
            auditorium.title = x.name
        raise web.seeother('/auditoriums')

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
        result = json.dumps(get_conflicts_json(x.code, x.session))
        return result

class parametrization:
    def POST(self):
        x = web.input()
        day1 = datetime.strptime(x.day1, '%d/%m/%Y')
        day2 = datetime.strptime(x.day2, '%d/%m/%Y')
        day3 = datetime.strptime(x.day3, '%d/%m/%Y')
        rooms = int(x.rooms)
        for i in range(1, rooms+1):
            Room(title="Auditoire"+str(i))
        Parametrization(rooms_number=rooms, day_1=day1, day_2=day2, day_3=day3, reserve=int(x.reserve)-1)
        return "ok"

class csv_export:
    def GET(self):
        export_data("static/")
        return "ok"

class excel_export:
    def GET(self):
        export_data_excel("static/")
        return "ok"

class set_conflict:
    def POST(self):
        x = web.input()
        tfe = Tfe.select(Tfe.q.code == x.code)[0]
        if x.conflict == "true":
            tfe.conflict = True
        else:
            tfe.conflict = False

class set_user:
    def POST(self):
        x = web.input()
        if User.select(User.q.email==x.email).count() == 0:
            pwdhash = hashlib.md5(x.password.encode('utf-8')).hexdigest()
            User(email=x.email, password=pwdhash, permission=int(x.permission))
        raise web.seeother('/index')


class reset_db:
    def GET(self):
        Sessions.dropTable(ifExists=True)
        Sessions.createTable()
        Disponibility.dropTable(ifExists=True)
        Disponibility.createTable()
        Student.dropTable(ifExists=True)
        Student.createTable()
        Person.dropTable(ifExists=True)
        Person.createTable()
        Tfe.dropTable(ifExists=True)
        Tfe.createTable()
        Tfe_rel_student.dropTable(ifExists=True)
        Tfe_rel_student.createTable()
        Tfe_rel_person.dropTable(ifExists=True)
        Tfe_rel_person.createTable()
        Room.dropTable(ifExists=True)
        Room.createTable()
        Parametrization.dropTable(ifExists=True)
        Parametrization.createTable()
        return "ok"

if __name__ == "__main__":
    app = web.application(urls, globals())
    db = web.database(dbn='sqlite', db='tfescheduler.db')
    store = web.session.DBStore(db, 'sessions')
    session = web.session.Session(app, store, initializer={'count': 0})
    app.add_processor(load_sqlo)
    app.run()