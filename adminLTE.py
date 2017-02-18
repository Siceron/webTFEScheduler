import web
import sys
import math
from models import *
from json_utils import *
from parser_utils import *
from subprocess import Popen, PIPE, STDOUT
import json
from pprint import pprint

render = web.template.render('templates/')

urls = (
    '/', 'index',
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

class index:

    def GET(self):
        tfe_nbr = Tfe.select().count()
        rooms = math.ceil(tfe_nbr/(3*12))
        return render.starter(rooms)

    def POST(self):
        """ Store csv file """
        x = web.input(myfile={})
        populate_db(x)
        raise web.seeother('/')

class executescheduler:
    def POST(self):
        x = web.input()
        with open("input.JSON", "w") as outfile:
            json.dump(create_input_json(x.rooms), outfile, indent=4)
        proc = Popen(["java", "-jar", "scheduler/TFEScheduler.jar", "input.JSON", x.time], stdout=PIPE, stderr=STDOUT)
        proc.wait()
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
        
class scheduler:
    def GET(self):
        tfes = Tfe.select()
        return render.scheduler(tfes)

class informations:
    def GET(self):
        students = Student.select()
        advisors = Advisor.select()
        tfes = Tfe.select()
        readers = Reader.select()
        return render.informations(students, advisors, tfes, readers)

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.add_processor(load_sqlo)
    app.run()