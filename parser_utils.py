import csv
import os
from random import randint
from models import *
from availabilities import set_availabilities
import re

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

def populate_db(input):
    filedir = 'files' # change this to the directory you want to store the file in.
    if 'myfile' in input: # to check if the file-object is created
        if input.myfile.filename == "":
            return "Erreur : Pas de fichier"
        filepath=input.myfile.filename.replace('\\','/') # replaces the windows-style slashes with linux ones.
        filename=filepath.split('/')[-1] # splits the and chooses the last part (the filename with extension)
        fout = open(filedir +'/'+ filename,'wb') # creates the file where the uploaded file should be stored
        fout.write(input.myfile.file.read()) # writes the uploaded file to the newly created file.
        fout.close() # closes the file, upload complete.

    random_disp = False
    if 'randomdisp' in input:
        random_disp = True

    return_result = "ok"

    """ Read csv file """
    header = True
    with open(filedir +'/'+ filename, 'rt') as f: # opens the csv file
        try:
            reader = csv.reader(f, delimiter=';')  # creates the reader object
            missing_count = 0
            for row in reader:   # iterates the rows of the file in orders
                if header:
                    if (row[0] != "Code" or row[1] != "Titre" or row[2] != "Etudiants" or row[3] != "Promoteurs" or row[4] != "Lecteurs" or row[21] != "Mails"):
                        print("hello")
                        return_result = "CSV header format not respected"
                        print(return_result)
                    header = False
                else:
                    #mails = row[20].split(" , ")
                    if Tfe.select(Tfe.q.code == row[0]).count() == 0:
                        confidential = False
                        cpme = False
                        open_hub = False
                        if row[5] == "y":
                            confidential = True
                        if row[6] == "y":
                            cpme = True
                        if row[7] == "y":
                            open_hub = True
                        memoire = Tfe(code=row[0], title=row[1], confidential=confidential, cpme=cpme, open_hub=open_hub)
                        emails = row[21].split(",")
                        email_count = 0
                        for etu in row[2].split(" - "):
                            etu_name = etu.split(", ")
                            etu_fac = etu_name[1].split(' ')
                            if Student.select(Student.q.email == emails[email_count].lower().strip()).count() == 0:
                                firstname = etu_name[1][:etu_name[1].find("(")-1]
                                fac = etu_name[1][etu_name[1].find("(")+1:etu_name[1].find(")")]
                                etudiant = Student(email=emails[email_count].lower().strip(), last_name=etu_name[0],name=firstname, faculty=fac)
                                tfe_rel_student = Tfe_rel_student(tfe=memoire, student=etudiant)
                            email_count += 1
                        if row[3] == "":
                            if random_disp==True:
                                person = Person(email="missing"+str(missing_count)+"@missing.com", last_name="missing",name="missing", disponibility=get_rand_disp())
                                tfe_rel_person = Tfe_rel_person(tfe=memoire, person=person, title="Promoteur")
                            else:
                                person = Person(email="missing"+str(missing_count)+"@missing.com", last_name="missing",name="missing", disponibility=Disponibility())
                                tfe_rel_person = Tfe_rel_person(tfe=memoire, person=person, title="Promoteur")
                            missing_count += 1
                        else:
                            for prom in re.sub(r'\([^)]*\)', '', row[3]).split(" - "):
                                prom_name = prom.split(", ")
                                if Person.select(Person.q.email == emails[email_count].lower().strip()).count() == 0:
                                    if len(prom_name) == 2:
                                        if random_disp==True:
                                            person = Person(email=emails[email_count].lower().strip(), last_name=prom_name[0],name=prom_name[1], disponibility=get_rand_disp())
                                            tfe_rel_person = Tfe_rel_person(tfe=memoire, person=person, title="Promoteur")   
                                        else:
                                            person = Person(email=emails[email_count].lower().strip(), last_name=prom_name[0],name=prom_name[1], disponibility=Disponibility())
                                            tfe_rel_person = Tfe_rel_person(tfe=memoire, person=person, title="Promoteur")
                                    else:
                                        prom_name = re.sub(r'\([^)]*\)', '', prom).split(" ")
                                        if random_disp==True:
                                            person = Person(email=emails[email_count].lower().strip(), last_name=" ".join(prom_name[1:]),name=prom_name[0], disponibility=get_rand_disp())
                                            tfe_rel_person = Tfe_rel_person(tfe=memoire, person=person, title="Promoteur")   
                                        else:
                                            person = Person(email=emails[email_count].lower().strip(), last_name=" ".join(prom_name[1:]),name=prom_name[0], disponibility=Disponibility())
                                            tfe_rel_person = Tfe_rel_person(tfe=memoire, person=person, title="Promoteur")
                                else:
                                    tfe_rel_person = Tfe_rel_person(tfe=memoire, person=Person.select(Person.q.email == emails[email_count].lower().strip())[0], title="Promoteur")
                                email_count += 1
                        if row[4] == "":
                            if random_disp==True:
                                person = Person(email="missing"+str(missing_count)+"@missing.com", last_name="missing",name="missing", disponibility=get_rand_disp())
                                tfe_rel_person = Tfe_rel_person(tfe=memoire, person=person, title="Lecteur")
                            else:
                                person = Person(email="missing"+str(missing_count)+"@missing.com", last_name="missing",name="missing", disponibility=Disponibility())
                                tfe_rel_person = Tfe_rel_person(tfe=memoire, person=person, title="Lecteur")
                            missing_count += 1
                        else:
                            for lect in re.sub(r'\([^)]*\)', '', row[4]).split(" - "):
                                lect_name = lect.split(", ")
                                if Person.select(Person.q.email == emails[email_count].lower().strip()).count() == 0:
                                    if len(lect_name) == 2:
                                        lect_descr = lect_name[1].split(' ')
                                        if random_disp==True:
                                            person = Person(email=emails[email_count].lower().strip(), last_name=lect_name[0],name=lect_descr[0], disponibility=get_rand_disp())
                                            tfe_rel_person = Tfe_rel_person(tfe=memoire, person=person, title="Lecteur")
                                        else:
                                            person = Person(email=emails[email_count].lower().strip(), last_name=lect_name[0],name=lect_descr[0], disponibility=Disponibility())
                                            tfe_rel_person = Tfe_rel_person(tfe=memoire, person=person, title="Lecteur")
                                        email_count += 1
                                    else:
                                        lect_name = lect.split(' ')
                                        if random_disp==True:
                                            person = Person(email=emails[email_count].lower().strip(), last_name=" ".join(lect_name[1:]),name=lect_name[0], disponibility=get_rand_disp())
                                            tfe_rel_person = Tfe_rel_person(tfe=memoire, person=person, title="Lecteur")
                                        else:
                                            person = Person(email=emails[email_count].lower().strip(), last_name=" ".join(lect_name[1:]),name=lect_name[0], disponibility=Disponibility())
                                            tfe_rel_person = Tfe_rel_person(tfe=memoire, person=person, title="Lecteur")
                                        email_count += 1
                                else:
                                    tfe_rel_person = Tfe_rel_person(tfe=memoire, person=Person.select(Person.q.email == emails[email_count].lower().strip())[0], title="Lecteur")
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
        except Exception as e:
            print("error")
            print(str(e))
            return_result = str(e)
        finally:
            f.close()      # closing
            os.remove(filedir +'/'+ filename)
            return return_result



def csv_availabalities_to_db(input):
    feedback = []
    filedir = 'files'  # change this to the directory you want to store the file in.
    if 'availabiltyfile' in input:  # to check if the file-object is created
        if input.availabiltyfile.filename == "":
            return "Erreur : Pas de fichier"
        filepath = input.availabiltyfile.filename.replace('\\', '/')  # replaces the windows-style slashes with linux ones.
        filename = filepath.split('/')[-1]  # splits the and chooses the last part (the filename with extension)
        fout = open(filedir + '/' + filename, 'wb')  # creates the file where the uploaded file should be stored
        fout.write(input.availabiltyfile.file.read())  # writes the uploaded file to the newly created file.
        fout.close()  # closes the file, upload complete.
    with open(filedir + '/' + filename, 'rt') as f:  # opens the csv file
        try:
            reader = csv.reader(f, delimiter=';')  # creates the reader object
            for elem in reader:
                feed = set_availabilities(elem)
                if feed !="":
                    feedback.append(feed + "\n")
            return feedback
        except:
            return "Erreur : Mauvais fichier"
        finally:
            f.close()  # closing
            os.remove(filedir + '/' + filename)
