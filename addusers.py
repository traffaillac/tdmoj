from os import system
from sys import stdin

for line in stdin:
	email, uid = line.rstrip().split(",")
	print(f"python3 manage.py adduser {uid} {email} {uid} PY3")
