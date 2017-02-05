import web
import csv
import sys
from models import *
from json_utils import *
from subprocess import Popen, PIPE, STDOUT
import json
from pprint import pprint
from random import randint

render = web.template.render('templates/')

urls = (
    '/', 'index',
    '/scheduler', 'scheduler',
    '/informations', 'informations',
    '/executescheduler', 'executescheduler'
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

def get_rand_bool():
    if(randint(0,3) == 0):
        return False
    else:
        return True

def get_rand_disp():
    disponibility = Disponibility(session_0=get_rand_bool(), session_1=get_rand_bool(), session_2=get_rand_bool(), session_3=get_rand_bool(),\
        session_4=get_rand_bool(), session_5=get_rand_bool(), session_6=get_rand_bool(), session_7=get_rand_bool(), session_8=get_rand_bool(),\
        session_9=get_rand_bool(), session_10=get_rand_bool(), session_11=get_rand_bool())
    return disponibility

class index:

    def GET(self):
        return render.starter()

    def POST(self):
        """ Store csv file """
        x = web.input(myfile={})
        filedir = 'files' # change this to the directory you want to store the file in.
        if 'myfile' in x: # to check if the file-object is created
            filepath=x.myfile.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
            filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
            fout = open(filedir +'/'+ filename,'wb') # creates the file where the uploaded file should be stored
            fout.write(x.myfile.file.read()) # writes the uploaded file to the newly created file.
            fout.close() # closes the file, upload complete.

        random_disp = False
        if 'randomdisp' in x:
            random_disp = True

        """ Read csv file """
        header = True
        f = open(filedir +'/'+ filename, 'rt') # opens the csv file
        try:
            reader = csv.reader(f, delimiter=';')  # creates the reader object
            for row in reader:   # iterates the rows of the file in orders
                if header:
                    header = False
                else:
                    if row[3] != "" and row[4] != "":
                        #mails = row[20].split(" , ")
                        if Tfe.select(Tfe.q.code == row[0]).count() == 0:
                            memoire = Tfe(code=row[0], title=row[1])
                            emails = row[20].split(" , ")
                            email_count = 0
                            for etu in row[2].split(" - "):
                                etu_name = etu.split(", ")
                                etu_fac = etu_name[1].split(' ')
                                if Student.select(Student.q.email == emails[email_count]).count() == 0:
                                    firstname = etu_name[1][:etu_name[1].find("(")-1]
                                    fac = etu_name[1][etu_name[1].find("(")+1:etu_name[1].find(")")]
                                    etudiant = Student(email=emails[email_count], last_name=etu_name[0],name=firstname, faculty=fac)
                                    tfe_rel_student = Tfe_rel_student(tfe=memoire, student=etudiant)
                                email_count += 1
                            for prom in row[3].split(" - "):
                                prom_name = prom.split(", ")
                                if Advisor.select(Advisor.q.email == emails[email_count]).count() == 0:
                                    if random_disp==True:
                                        promoteur = Advisor(email=emails[email_count], last_name=prom_name[0],name=prom_name[1], disponibility=get_rand_disp())
                                        tfe_rel_advisor = Tfe_rel_advisor(tfe=memoire, advisor=promoteur)
                                    else:
                                        promoteur = Advisor(email=emails[email_count], last_name=prom_name[0],name=prom_name[1], disponibility=Disponibility())
                                        tfe_rel_advisor = Tfe_rel_advisor(tfe=memoire, advisor=promoteur)
                                email_count += 1
                            for lect in row[4].split(" - "):
                                lect_name = lect.split(", ")
                                if len(lect_name) == 2:
                                    if Reader.select(Reader.q.email == emails[email_count]).count() == 0:
                                        if len(lect_name) == 2:
                                            lect_descr = lect_name[1].split(' ')
                                            if random_disp==True:
                                                lecteur = Reader(email=emails[email_count], last_name=lect_name[0],name=lect_descr[0], disponibility=get_rand_disp())
                                                tfe_rel_reader = Tfe_rel_reader(tfe=memoire, reader=lecteur)
                                            else:
                                                lecteur = Reader(email=emails[email_count], last_name=lect_name[0],name=lect_descr[0], disponibility=Disponibility())
                                                tfe_rel_reader = Tfe_rel_reader(tfe=memoire, reader=lecteur)
                                            email_count += 1
                                        else:
                                            lect_name = lect.split(' ')
                                            if len(lect_name) == 4 or len(lect_name) == 3:
                                                if random_disp==True:
                                                    lecteur = Reader(email=emails[email_count], last_name=lect_name[2],name=lect_name[1], disponibility=get_rand_disp())
                                                    tfe_rel_reader = Tfe_rel_reader(tfe=memoire, reader=lecteur)
                                                else:
                                                    lecteur = Reader(email=emails[email_count], last_name=lect_name[2],name=lect_name[1], disponibility=Disponibility())
                                                    tfe_rel_reader = Tfe_rel_reader(tfe=memoire, reader=lecteur)
                                                email_count += 1
                                            else:
                                                print("discarded : "+row[0])
                                    else:
                                        email_count += 1
                            """print(row[0])
                            print(row[1])
                            print(row[2])
                            print(row[3])
                            print(row[4])
                            print(row[9])
                            print(row[10])
                            print(row[11])
                            print(row[12])
                            print(row[13])
                            print(row[14])
                            print(row[15])
                            print(row[16])
                            print(row[17])
                            print(row[18])
                            print(row[19])
                            print(row[20])"""
                    else:
                        print("discarded : "+row[0])
        finally:
            f.close()      # closing
        raise web.seeother('/')

class executescheduler:
    def GET(self):
        with open("input.JSON", "w") as outfile:
            json.dump(create_input_json(), outfile, indent=4)
        proc = Popen(["java", "-jar", "scheduler/TFEScheduler.jar", "input.JSON", "1"], stdout=PIPE, stderr=STDOUT)
        proc.wait()
        for line in proc.stdout:
            print(line)

        with open('output.JSON') as data_file:    
            data = json.load(data_file)

        for i in data:
            tfe = Tfe.select(Tfe.q.code == i["code"])[0]
            tfe.session=i["session"]
        
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