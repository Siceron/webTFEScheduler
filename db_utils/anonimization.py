from models import *

sqlhub.processConnection = connectionForURI('sqlite:tfescheduler.db')

def modify_tfe():
	tfes = Tfe.select()
	i = 0
	for tfe in tfes:
		tfe.title = "title"+str(i)
		i+=1

def modify_student():
	students = Student.select()
	i = 0
	for student in students:
		student.email = "student"+str(i)+"@student.uclouvain.be"
		student.name = "firstname"+str(i)
		student.last_name = "lastname"+str(i)
		i+=1

def modify_person():
	persons = Person.select()
	i = 0
	for person in persons:
		person.email = "jury"+str(i)+"@uclouvain.be"
		person.name = "firstname"+str(i)
		person.last_name = "lastname"+str(i)
		i+=1

if __name__ == "__main__":
	modify_tfe()
	modify_student()
	modify_person()

