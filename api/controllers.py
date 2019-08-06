import pymysql
from dotenv import load_dotenv
import os
from collections import namedtuple

load_dotenv()

db = pymysql.connect(
	os.getenv("DB_HOST"),
	os.getenv("DB_USER"),
	os.getenv("DB_PASS"),
	os.getenv("DB_NAME")
)
cursor = db.cursor()

def getUsers():
	cursor.execute("select * from users")
	users = cursor.fetchall()
	return users

def getEvents():
    events = []
    cursor.execute("select e.name, v.name, e.date, e.capacity from events e join venues v on e.venue=v.id")
    result = cursor.fetchall()
    for item in result:
        EventRecord = namedtuple("EventRecord", "name, venue, date, capacity")
        event = EventRecord._make(item)
        events.append(event)
    return events

def isAdmin(name):
	cursor.execute(
		"""
		select name from roles
		join users on roles.id = users.role
		where users.user = ?
		""", (name,)
	)
	result = cursor.fetchone()
	return True if result and result[0] == "admin" else False

def findUser(name):
	cursor.execute("select * from users where user = ?", (name,))
	result = cursor.fetchone()
	return result[1] if result else None

def addUser(name, role, user):
	if not isAdmin(user):
		print('you are not allowed to perform this action')
		return None

	found = findUser(name)
	if not found:
		cursor.execute("select id from roles where name = ?", (role,))
		result = cursor.fetchone()

	if not result:
		print("not a valid role")
		return None

	roleNum = result[0]
	cursor.execute("insert into users(user, role) values(?, ?)", (name, roleNum))
	rows = cursor.rowcount
	if rows == 1:
		db.commit()
		print("User '" + name + "' has been added succesfully.")
	else:
		print("User not added")
		db.rollback()

	return None
