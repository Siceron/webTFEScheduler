from sqlobject import *
import hashlib

sqlhub.processConnection = connectionForURI('sqlite:tfescheduler.db')

class User(SQLObject):

	class sqlmeta:
		table = 'user'

	email = StringCol()
	password = StringCol()

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

class Advisor(SQLObject):

	class sqlmeta:
		table = 'advisor'

	email = StringCol(unique=True)
	name = StringCol()
	last_name = StringCol()
	faculty = StringCol(default='UNK')
	disponibility = ForeignKey('Disponibility')

class Reader(SQLObject):

	class sqlmeta:
		table = 'reader'

	email = StringCol(unique=True)
	name = StringCol()
	last_name = StringCol()
	faculty = StringCol(default='UNK')
	disponibility = ForeignKey('Disponibility')

class Tfe(SQLObject):

	class sqlmeta:
		table = 'tfe'

	code = StringCol(unique=True)
	title = StringCol()
	session = IntCol(default=-1)
	commission = StringCol(default=None, notNone=False)

class Tfe_rel_student(SQLObject):

	class sqlmeta:
		table = 'tfe_rel_student'

	tfe = ForeignKey('Tfe')
	student = ForeignKey('Student')

class Tfe_rel_advisor(SQLObject):

	class sqlmeta:
		table = 'tfe_rel_advisor'

	tfe = ForeignKey('Tfe')
	advisor = ForeignKey('Advisor')

class Tfe_rel_reader(SQLObject):

	class sqlmeta:
		table = 'tfe_rel_reader'

	tfe = ForeignKey('Tfe')
	reader = ForeignKey('Reader')

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
	Advisor.dropTable(ifExists=True)
	Advisor.createTable()
	Reader.dropTable(ifExists=True)
	Reader.createTable()
	Tfe.dropTable(ifExists=True)
	Tfe.createTable()
	Tfe_rel_student.dropTable(ifExists=True)
	Tfe_rel_student.createTable()
	Tfe_rel_advisor.dropTable(ifExists=True)
	Tfe_rel_advisor.createTable()
	Tfe_rel_reader.dropTable(ifExists=True)
	Tfe_rel_reader.createTable()