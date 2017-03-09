import json
from models import *

def advisors_json():
    advisors_as_dict = []
    for rel in Tfe_rel_person.select(Tfe_rel_person.q.title == "Promoteur"):
        advisor_as_dict = {
            "email" : rel.person.email,
            "faculty" : "UNK",
            "disponibilities": [
                rel.person.disponibility.session_0,
                rel.person.disponibility.session_1,
                rel.person.disponibility.session_2,
                rel.person.disponibility.session_3,
                rel.person.disponibility.session_4,
                rel.person.disponibility.session_5,
                rel.person.disponibility.session_6,
                rel.person.disponibility.session_7,
                rel.person.disponibility.session_8,
                rel.person.disponibility.session_9,
                rel.person.disponibility.session_10,
                rel.person.disponibility.session_11
            ]
        }
        advisors_as_dict.append(advisor_as_dict)
    return advisors_as_dict

def readers_json():
    readers_as_dict = []
    for rel in Tfe_rel_person.select(Tfe_rel_person.q.title == "Lecteur"):
        reader_as_dict = {
            "email" : rel.person.email,
            "faculty" : "UNK",
            "disponibilities": [
                rel.person.disponibility.session_0,
                rel.person.disponibility.session_1,
                rel.person.disponibility.session_2,
                rel.person.disponibility.session_3,
                rel.person.disponibility.session_4,
                rel.person.disponibility.session_5,
                rel.person.disponibility.session_6,
                rel.person.disponibility.session_7,
                rel.person.disponibility.session_8,
                rel.person.disponibility.session_9,
                rel.person.disponibility.session_10,
                rel.person.disponibility.session_11
            ]
        }
        readers_as_dict.append(reader_as_dict)
    return readers_as_dict

def tfes_json():
    tfes_as_dict = []
    for tfe in Tfe.select():
        students = []
        for rel in Tfe_rel_student.select(Tfe_rel_student.q.tfe==tfe):
            student = {
                "email" : rel.student.email,
                "faculty" : rel.student.faculty
            }
            students.append(student)
        advisors = []
        for rel in Tfe_rel_person.select(AND(Tfe_rel_person.q.tfe==tfe, Tfe_rel_person.q.title=="Promoteur")):
            advisor = {
                "email" : rel.person.email,
                "faculty" : "UNK"
            }
            advisors.append(advisor)
        readers = []
        for rel in Tfe_rel_person.select(AND(Tfe_rel_person.q.tfe==tfe, Tfe_rel_person.q.title=="Lecteur")):
            reader = {
                "email" : rel.person.email,
                "faculty" : "UNK"
            }
            readers.append(reader)
        tfe_as_dict = {
            "code" : tfe.code,
            "students" : students,
            "advisors" : advisors,
            "readers" : readers
        }
        tfes_as_dict.append(tfe_as_dict)
    return tfes_as_dict

def fixed_json():
    fixeds_as_dict = []
    for tfe in Tfe.select():
        if tfe.session != -1:
            fixed_as_dict = {
                "code" : tfe.code,
                "session" : tfe.session
            }
            fixeds_as_dict.append(fixed_as_dict)
    return fixeds_as_dict

def create_input_json(rooms):

    advisors = advisors_json()
    readers = readers_json()
    tfes = tfes_json()
    fixed = fixed_json()
    json = {
        "sessionNumber": int(rooms)*12,
        "sessionDays": 3,
        "sessionRooms": int(rooms),
        "advisors" : advisors,
        "readers" : readers,
        "tfes" : tfes,
        "banned" : [],
        "fixed" : fixed
    }
    return json