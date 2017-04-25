from models import *
import sys

def set_availabilities(person_email, s0, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11):
    person = Person.select(Person.q.email == person_email)[0]
    person.disponibility.session_0 = s0 == "True"
    person.disponibility.session_1 = s1 == "True"
    person.disponibility.session_2 = s2 == "True"
    person.disponibility.session_3 = s3 == "True"
    person.disponibility.session_4 = s4 == "True"
    person.disponibility.session_5 = s5 == "True"
    person.disponibility.session_6 = s6 == "True"
    person.disponibility.session_7 = s7 == "True"
    person.disponibility.session_8 = s8 == "True"
    person.disponibility.session_9 = s9 == "True"
    person.disponibility.session_10 = s10 == "True"
    person.disponibility.session_11 = s11 == "True"

if __name__ == "__main__":
    if len(sys.argv) == 14:
        set_availabilities(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], \
            sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10], sys.argv[11], sys.argv[12], sys.argv[13])
    else:
        print("Not enough args")