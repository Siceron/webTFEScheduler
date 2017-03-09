from sqlobject import *
import hashlib

sqlhub.processConnection = connectionForURI('sqlite:tfescheduler.db')

class User(SQLObject):

	class sqlmeta:
		table = 'user'

	email = StringCol()
	password = StringCol()
	permission = IntCol(default=0)

class Sessions(SQLObject):

	class sqlmeta:
		table = 'sessions'

	session_id = StringCol(length=128, unique=True, notNone=True)
	atime = TimestampCol(notNone=True, default=DateTimeCol.now)
	data = StringCol()

class Secretary(SQLObject):

	class sqlmeta:
		table = 'secretary'

	email = StringCol(unique=True)
	name = StringCol()
	last_name = StringCol()

class Secretary_faculty(SQLObject):

	class sqlmeta:
		table = 'secretary_faculty'

	faculty = StringCol(unique=True)
	secretary = ForeignKey('Secretary')

class Secretary_tfe(SQLObject):

	class sqlmeta:
		table = 'secretary_tfe'

	secretary = ForeignKey('Secretary')
	tfe = ForeignKey('Tfe')

class Disponibility(SQLObject):

	class sqlmeta:
		table = 'disponibility'

	session_0 = BoolCol(default=False)
	session_1 = BoolCol(default=False)
	session_2 = BoolCol(default=False)
	session_3 = BoolCol(default=False)
	session_4 = BoolCol(default=False)
	session_5 = BoolCol(default=False)
	session_6 = BoolCol(default=False)
	session_7 = BoolCol(default=False)
	session_8 = BoolCol(default=False)
	session_9 = BoolCol(default=False)
	session_10 = BoolCol(default=False)
	session_11 = BoolCol(default=False)

class Student(SQLObject):

	class sqlmeta:
		table = 'student'

	email = StringCol(unique=True)
	name = StringCol()
	last_name = StringCol()
	faculty = StringCol()

class Person(SQLObject):

	class sqlmeta:
		table = 'person'

	email = StringCol(unique=True)
	name = StringCol()
	last_name = StringCol()
	disponibility = ForeignKey('Disponibility')

class Tfe(SQLObject):

	class sqlmeta:
		table = 'tfe'

	code = StringCol(unique=True)
	title = StringCol()
	session = IntCol(default=-1)
	commission = StringCol(default="TBD", notNone=False)
	moderator = StringCol(default=None)
	log = TimestampCol(notNone=True, default=DateTimeCol.now)

class Tfe_rel_student(SQLObject):

	class sqlmeta:
		table = 'tfe_rel_student'

	tfe = ForeignKey('Tfe')
	student = ForeignKey('Student')

class Tfe_rel_person(SQLObject):

	class sqlmeta:
		table = 'tfe_rel_person'

	tfe = ForeignKey('Tfe')
	person = ForeignKey('Person')
	title = StringCol()

class Room(SQLObject):

	class sqlmeta:
		table = 'room'

	title = StringCol()

if __name__ == "__main__":
	User.dropTable(ifExists=True)
	User.createTable()
	Sessions.dropTable(ifExists=True)
	Sessions.createTable()
	pwdhash = hashlib.md5("pass".encode('utf-8')).hexdigest()
	user = User(email="admin@a.com", password=pwdhash)
	Disponibility.dropTable(ifExists=True)
	Disponibility.createTable()
	Student.dropTable(ifExists=True)
	Student.createTable()
	Person.dropTable(ifExists=True)
	Person.createTable()
	Tfe.dropTable(ifExists=True)
	Tfe.createTable()
	Tfe_rel_student.dropTable(ifExists=True)
	Tfe_rel_student.createTable()
	Tfe_rel_person.dropTable(ifExists=True)
	Tfe_rel_person.createTable()
	Room.dropTable(ifExists=True)
	Room.createTable()