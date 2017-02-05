import json
from models import *

def advisors_json():
    advisors_as_dict = []
    for advisor in Advisor.select():
        advisor_as_dict = {
            "email" : advisor.email,
            "faculty" : advisor.faculty,
            "disponibilities": [
                advisor.disponibility.session_0,
                advisor.disponibility.session_1,
                advisor.disponibility.session_2,
                advisor.disponibility.session_3,
                advisor.disponibility.session_4,
                advisor.disponibility.session_5,
                advisor.disponibility.session_6,
                advisor.disponibility.session_7,
                advisor.disponibility.session_8,
                advisor.disponibility.session_9,
                advisor.disponibility.session_10,
                advisor.disponibility.session_11
            ]
        }
        advisors_as_dict.append(advisor_as_dict)
    return advisors_as_dict

def readers_json():
    readers_as_dict = []
    for reader in Reader.select():
        reader_as_dict = {
            "email" : reader.email,
            "faculty" : reader.faculty,
            "disponibilities": [
                reader.disponibility.session_0,
                reader.disponibility.session_1,
                reader.disponibility.session_2,
                reader.disponibility.session_3,
                reader.disponibility.session_4,
                reader.disponibility.session_5,
                reader.disponibility.session_6,
                reader.disponibility.session_7,
                reader.disponibility.session_8,
                reader.disponibility.session_9,
                reader.disponibility.session_10,
                reader.disponibility.session_11
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
        for rel in Tfe_rel_advisor.select(Tfe_rel_advisor.q.tfe==tfe):
            advisor = {
                "email" : rel.advisor.email,
                "faculty" : rel.advisor.faculty
            }
            advisors.append(advisor)
        readers = []
        for rel in Tfe_rel_reader.select(Tfe_rel_reader.q.tfe==tfe):
            reader = {
                "email" : rel.reader.email,
                "faculty" : rel.reader.faculty
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

def secretaries_json():
    secretaries_as_dict = [
        {
          "email": "secretary1@uclouvain.be",
          "faculties": [
            "ELEC",
            "ELME",
            "GBIO"
          ],
          "tfes": []
        },
        {
          "email": "secretary2@uclouvain.be",
          "faculties": [
            "FYAP",
            "KIMA"
          ],
          "tfes": []
        },
        {
          "email": "secretary3@uclouvain.be",
          "faculties": [
            "GCE"
          ],
          "tfes": []
        },
        {
          "email": "secretary4@uclouvain.be",
          "faculties": [
            "INFO",
            "SINF"
          ],
          "tfes": []
        },
        {
          "email": "secretary5@uclouvain.be",
          "faculties": [
            "MAP"
          ],
          "tfes": []
        },
        {
          "email": "secretary6@uclouvain.be",
          "faculties": [
            "MECA"
          ],
          "tfes": []
        },
        {
          "email": "secretary-poubelle@uclouvain.be",
          "faculties": [
            "UNK"
          ],
          "tfes": []
        }
    ]
    return secretaries_as_dict

def create_input_json():

    advisors = advisors_json()
    readers = readers_json()
    secretaries = secretaries_json()
    tfes = tfes_json()
    json = {
        "sessionNumber": 60,
        "sessionDays": 3,
        "sessionRooms": 5,
        "secretaries": secretaries,
        "advisors" : advisors,
        "readers" : readers,
        "tfes" : tfes,
        "banned" : [],
        "fixed" : []
    }
    return json