from models import User
import sys, hashlib

def new_user():
	if len(sys.argv) == 3:
		pwdhash = hashlib.md5(sys.argv[2].encode('utf-8')).hexdigest()
		user = User(email=sys.argv[1], password=pwdhash)
	else:
		print("python3 add_user.py <email> <password>")

if __name__ == "__main__":
	new_user()