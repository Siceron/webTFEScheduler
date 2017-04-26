from models import *
import sys
import logging

def set_availabilities(table):
    logging.basicConfig(filename='setavailabilities.log', level=logging.DEBUG)
    mail = table[0]
    mail = mail.lower()
    mail = mail.strip()
    mail = mail.replace(" ", "")
    person = Person.select(Person.q.email == mail).getOne(None)
    if person is None:
        logging.info('The email ' + mail+' is not present in the database' )
    else:
        person.disponibility.session_0 = table[1] == "True"
        person.disponibility.session_1 = table[2] == "True"
        person.disponibility.session_2 = table[3] == "True"
        person.disponibility.session_3 = table[4] == "True"
        person.disponibility.session_4 = table[5] == "True"
        person.disponibility.session_5 = table[6] == "True"
        person.disponibility.session_6 = table[7] == "True"
        person.disponibility.session_7 = table[8] == "True"
        person.disponibility.session_8 = table[9] == "True"
        person.disponibility.session_9 = table[10] == "True"
        person.disponibility.session_10 = table[11] == "True"
        person.disponibility.session_11 = table[12] == "True"


if __name__ == "__main__":
    if len(sys.argv) == 14:
        set_availabilities(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], \
                           sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10], sys.argv[11], sys.argv[12],
                           sys.argv[13])
    else:
        print("Not enough args")
