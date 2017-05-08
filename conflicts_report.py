import json
from models import *

is_conflicts = False

def get_tfe_dictionnary():
    dictionnary = dict()
    tfes = Tfe.select()
    for tfe in tfes:
        if tfe.session in dictionnary:
            dictionnary[tfe.session].append(tfe.code)
        else:
            dictionnary[tfe.session] = []
            dictionnary[tfe.session].append(tfe.code)
    return dictionnary

def max_tfes_json(session):
    tfe_dictionnary = get_tfe_dictionnary()
    if session in tfe_dictionnary and len(tfe_dictionnary[session]) == 3:
        global is_conflicts
        is_conflicts = True
        return True
    return False

def get_disponibility(disponibility):
    result = []
    result.append(disponibility.session_0)
    result.append(disponibility.session_1)
    result.append(disponibility.session_2)
    result.append(disponibility.session_3)
    result.append(disponibility.session_4)
    result.append(disponibility.session_5)
    result.append(disponibility.session_6)
    result.append(disponibility.session_7)
    result.append(disponibility.session_8)
    result.append(disponibility.session_9)
    result.append(disponibility.session_10)
    result.append(disponibility.session_11)
    return result

def not_disponible_json(code, session):
    tfe = Tfe.select(Tfe.q.code == code)[0]
    rels = Tfe_rel_person.select(Tfe_rel_person.q.tfe == tfe)
    not_disponible_list = []
    for rel in rels:
        disponibility = get_disponibility(rel.person.disponibility)
        if disponibility[session%12] == False:
            global is_conflicts
            is_conflicts = True
            not_disponible = {
                "email" : rel.person.email,
                "prevented" : rel.prevented
            }
            not_disponible_list.append(not_disponible)
    return not_disponible_list

def is_conflicts_after_person_modifs(rel):
    disponibility = get_disponibility(rel.person.disponibility)
    return (disponibility[rel.tfe.session%12] == False)

def get_person_dictionnary(code):
    dictionnary = dict()
    from_tfe = Tfe.select(Tfe.q.code == code)[0].code
    tfes = Tfe.select()
    for tfe in tfes:
        rels = Tfe_rel_person.select(Tfe_rel_person.q.tfe == tfe)
        if tfe.code != from_tfe:
            if tfe.session in dictionnary:
                for rel in rels:    
                    dictionnary[tfe.session].append(rel.person.email)
            else:
                dictionnary[tfe.session] = []
                for rel in rels:    
                    dictionnary[tfe.session].append(rel.person.email)
    return dictionnary

def parallel_json(code, session, rooms):
    person_dictionnary = get_person_dictionnary(code)
    tfe = Tfe.select(Tfe.q.code == code)[0]
    rels = Tfe_rel_person.select(Tfe_rel_person.q.tfe == tfe)
    parallel_list = []
    for rel in rels:
        for i in range(0, rooms):
            if session != (session%12)+(i*12) and (session%12)+(i*12) in person_dictionnary and rel.person.email in person_dictionnary[(session%12)+(i*12)]:
                global is_conflicts
                is_conflicts = True
                parallel = {
                    "email" : rel.person.email,
                    "prevented" : rel.prevented
                }
                parallel_list.append(parallel)
                break
    return parallel_list


def get_conflicts_json(code, session):
    global is_conflicts
    is_conflicts = False
    max_tfes = max_tfes_json(int(session))
    not_disponible = not_disponible_json(code, int(session))
    parallel = parallel_json(code, int(session), 5)
    result = {
        "is_conflicts": is_conflicts,
        "max_tfes": max_tfes,
        "not_disponible": not_disponible,
        "parallel": parallel
    }
    return result