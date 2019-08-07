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
    cursor.execute("select e.name, v.name, e.datetime, e.capacity from events e join venues v on e.venue=v.id")
    result = cursor.fetchall()
    for item in result:
        EventRecord = namedtuple("EventRecord", "name, venue, datetime, capacity")
        event = EventRecord._make(item)
        events.append(event)
    return events

def isAdmin(name):
	cursor.execute(
		"""
		select name from roles
		join users on roles.id = users.role
		where users.user = %s
		""", (name,)
	)
	result = cursor.fetchone()
	return True if result and result[0] == "admin" else False

def findUser(name):
	cursor.execute("select * from users where user = %s", (name,))
	result = cursor.fetchone()
	return result[1] if result else None

def addUser(username, password, role):
	cursor.execute(
		"""insert into users(username, password, role) values(%s, %s, 
		(select id from roles where name = %s)
		)""",
		(username, password, role))
	rows = cursor.rowcount

	if not rows == 1:
		db.rollback()
		raise Exception('User not added')

	db.commit()
	msg = 'User {} has been added successfully'.format(username)
	return msg
