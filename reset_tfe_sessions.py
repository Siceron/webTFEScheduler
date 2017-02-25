from models import *

sqlhub.processConnection = connectionForURI('sqlite:tfescheduler.db')

if __name__ == "__main__":
	tfes = Tfe.select()
	for tfe in tfes:
		tfe.session = -1