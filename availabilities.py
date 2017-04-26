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
        return 'The email ' + mail+' is not present in the database'
    else:
        f=''
        allTrue = True
        identique = True
        for key,value in vars(person.disponibility).items():
            if '_SO_val_session' in key:
                i = key[-2:].replace("_","")
                i= int(i)
                if not value:
                    allTrue=False
                val = (table[i+1] == "True" or table[i+1]=="TRUE" or table[i+1]=="true" or table[i+1]=="1" or table[i+1]=="ok")
                if str(value) !=str(val):
                    print("check")
                    print(value)
                    print(table[i+1])
                    print("end")
                    identique=False
                    logging.info(mail + ' : mise à jour')
                    f = mail + ' : mise à jour'
                    break
        if not allTrue and identique:
            f = "Aucun changement"

        if allTrue or not identique:
            person.disponibility.session_0 = (table[1] == "True" or table[1]=="TRUE" or table[1]=="true" or table[1]=="1" or table[1]=="ok")
            person.disponibility.session_1 = (table[2] == "True" or table[2]=="TRUE" or table[2]=="true" or table[2]=="1" or table[2]=="ok")
            person.disponibility.session_2 = (table[3] == "True" or table[3]=="TRUE" or table[3]=="true" or table[3]=="1" or table[3]=="ok")
            person.disponibility.session_3 = (table[4] == "True" or table[4]=="TRUE" or table[4]=="true" or table[4]=="1" or table[4]=="ok")
            person.disponibility.session_4 = (table[5] == "True" or table[5]=="TRUE" or table[5]=="true" or table[5]=="1" or table[5]=="ok")
            person.disponibility.session_5 = (table[6] == "True" or table[6]=="TRUE" or table[6]=="true" or table[6]=="1" or table[6]=="ok")
            person.disponibility.session_6 = (table[7] == "True" or table[7]=="TRUE" or table[7]=="true" or table[7]=="1" or table[7]=="ok")
            person.disponibility.session_7 = (table[8] == "True" or table[8]=="TRUE" or table[8]=="true" or table[8]=="1" or table[8]=="ok")
            person.disponibility.session_8 = (table[9] == "True" or table[9]=="TRUE" or table[9]=="true" or table[9]=="1" or table[9]=="ok")
            person.disponibility.session_9 = (table[10] == "True" or table[10]=="TRUE" or table[10]=="true" or table[10]=="1" or table[10]=="ok")
            person.disponibility.session_10 = (table[11] == "True" or table[11]=="TRUE" or table[11]=="true" or table[11]=="1" or table[11]=="ok")
            person.disponibility.session_11 = (table[12] == "True" or table[12]=="TRUE" or table[12]=="true" or table[12]=="1" or table[12]=="ok")
        return f

# if __name__ == "__main__":
#     if len(sys.argv) == 14:
#         set_availabilities(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5], sys.argv[6], \
#                            sys.argv[7], sys.argv[8], sys.argv[9], sys.argv[10], sys.argv[11], sys.argv[12],
#                            sys.argv[13])
#     else:
#         print("Not enough args")
