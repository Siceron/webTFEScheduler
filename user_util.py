from models import User
import sys, hashlib

def show_users():
	users = User.select()
	for user in users:
		print(user.email)

def suppress_user():
	if len(sys.argv) == 3:
		user = User.select(User.q.email == sys.argv[2])[0]
		user.delete(user.id)
		print("User "+sys.argv[2]+" deleted")
	else:
		print("python3 user_util.py -del <email>")

def new_user():
	if len(sys.argv) == 4:
		pwdhash = hashlib.md5(sys.argv[3].encode('utf-8')).hexdigest()
		user = User(email=sys.argv[2], password=pwdhash)
		print("User "+sys.argv[2]+" added")
	else:
		print("python3 user_util.py -add <email> <password>")

if __name__ == "__main__":
    if len(sys.argv) >= 2:
    	if sys.argv[1] == "-ls":
    		show_users()
    	elif sys.argv[1] == "-del":
    		suppress_user()
    	elif sys.argv[1] == "-add":
    		new_user()
    	else:
    		print("python3 user_util.py -ls")
    		print("python3 user_util.py -del <email>")
    		print("python3 user_util.py -add <email> <password>")