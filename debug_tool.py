from models import *

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

def show_tfes_in_conflict():
    conflicts = False
    for tfe in Tfe.select():
        conflicts = False
        session = tfe.session

        if session != -1:

            # For availabilities
            rels = Tfe_rel_person.select(Tfe_rel_person.q.tfe == tfe)
            not_disponible_list = []
            for rel in rels:
                if rel.prevented == False:
                    disponibility = get_disponibility(rel.person.disponibility)
                    if disponibility[session%12] == False:
                        conflicts = True
                        not_disponible_list.append(rel.person.email)

            # For parallel
            person_dictionnary = get_person_dictionnary(tfe.code)
            rels = Tfe_rel_person.select(Tfe_rel_person.q.tfe == tfe)
            parallel_list = []
            for rel in rels:
                if rel.prevented == False:
                    for i in range(0, Parametrization.select()[0].rooms_number):
                        if session != (session%12)+(i*12) and (session%12)+(i*12) in person_dictionnary and rel.person.email in person_dictionnary[(session%12)+(i*12)]:
                            conflicts = True
                            for t in Tfe.select(Tfe.q.session == (session%12)+(i*12)):
                                if Tfe_rel_person.select(AND(Tfe_rel_person.q.person == rel.person, Tfe_rel_person.q.tfe == t)).count() != 0:
                                    parallel_list.append(rel.person.email+" from "+t.code)

            if conflicts:
                print(tfe.code+" : ")
                for j in parallel_list:
                    print("\t - "+j)
                print("")

show_tfes_in_conflict()