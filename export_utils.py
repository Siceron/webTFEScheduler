from models import *
from datetime import datetime
import os
import glob
import csv
import openpyxl
import math

def check_none(element):
    return '' if element is None else str(element)

def get_day(session):
    modulo = session % 12
    if session == -1:
        return "TBD"
    elif modulo >= 0 and modulo <= 3:
        return str(Parametrization.select()[0].day_1.strftime('%d-%m-%Y'))
    elif modulo >= 4 and modulo <= 7:
        return str(Parametrization.select()[0].day_2.strftime('%d-%m-%Y'))
    elif modulo >= 8 and modulo <= 11:
        return str(Parametrization.select()[0].day_3.strftime('%d-%m-%Y'))

def get_hour(session):
    modulo = session % 12
    if session == -1:
        return "TBD"
    elif modulo == 0 or modulo == 4 or modulo == 8:
        return "8h"
    elif modulo == 1 or modulo == 5 or modulo == 9:
        return "10h45"
    elif modulo == 2 or modulo == 6 or modulo == 10:
        return "14h"
    else:
        return "16h45"

def get_auditorium(session):
    return Room.select()[math.floor(session/12)].title

def export_data(path):
    rows = []
    rows.append("Code;Titre;Etudiants;Promoteurs;Lecteurs;Mails;Modérateur;Commission;Jour;Heure;Auditoire;Confidentiel;CPME;OpenHub")
    for tfe in Tfe.select():
        emails = []
        students = []
        for rel in Tfe_rel_student.select(Tfe_rel_student.q.tfe==tfe):
            students.append(rel.student.last_name+", "+rel.student.name+" ("+rel.student.faculty+")")
            emails.append(rel.student.email)
        advisors = []
        for rel in Tfe_rel_person.select(AND(Tfe_rel_person.q.tfe==tfe, Tfe_rel_person.q.title=="Promoteur")):
            advisors.append(rel.person.last_name+", "+rel.person.name)
            emails.append(rel.person.email)
        readers = []
        for rel in Tfe_rel_person.select(AND(Tfe_rel_person.q.tfe==tfe, Tfe_rel_person.q.title=="Lecteur")):
            readers.append(rel.person.last_name+", "+rel.person.name)
            emails.append(rel.person.email)
        row = tfe.code+";"+tfe.title+";"+" - ".join(students)+";"+" - ".join(advisors)+";"+" - ".join(readers)+";"+\
            " , ".join(emails)+";"+check_none(tfe.moderator)+";"+tfe.commission+";"+get_day(tfe.session)+";"+get_hour(tfe.session)+";"+\
            get_auditorium(tfe.session)+";"+str(tfe.confidential)+";"+str(tfe.cpme)+";"+str(tfe.open_hub)
        rows.append(row)
    with open(path+"data.csv", 'w') as outfile:
        for row in rows:
            outfile.write(row+"\n")

def export_data_excel(path):
    export_data(path)
    f = open(path+"data.csv")
    wb = openpyxl.Workbook()
    ws = wb.active
    reader = csv.reader(f, delimiter=';')
    for i in reader:
        ws.append(i)
    f.close()
    wb.save(path+"data.xlsx")