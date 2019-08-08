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
    cursor.execute("select e.id, e.name, v.name, e.datetime, e.capacity, convert(e.description using utf8) from events e join venues v on e.venue=v.id")
    result = cursor.fetchall()
    for item in result:
        EventRecord = namedtuple("EventRecord", "id, name, venue, datetime, capacity, description")
        event = EventRecord._make(item)
        events.append(event)
    return events

def getEvent(eventId):
    cursor.execute("select e.name, v.name, e.datetime, e.capacity, convert(e.description using utf8) from events e join venues v on e.venue = v.id where %s = e.id", (eventId,))
    result = cursor.fetchone()
    EventRecord = namedtuple("EventRecord", "name, venue, datetime, capacity, description")
    event = EventRecord._make(result)
    return event

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
	msg = "User {} has been added successfully".format(username)
	return msg

def loginUser(username, password):
	cursor.execute(
		"""
		select u.id, u.username, r.name from users u
		join roles r on u.role = r.id
		where username = %s and password = %s
		""", (username, password)
	)
	result = cursor.fetchone()
	if not result:
		return {}

	return {
		"id": result[0],
		"username": result[1],
		"role": result[2]
	}

def joinEvent(userId, eventId):
	cursor.execute(
		"insert into usersEvents(userId, eventId) values(%s, %s)", (userId, eventId)
	)

	rows = cursor.rowcount
	if not rows == 1:
		db.rollback()
		raise Exception('User could not join event')

	db.commit()
	msg = "User has successfully joined the event"
	return msg

def getCapacityByEventId(eventId):
	cursor.execute("select capacity from events where id = %s", (eventId,))
	result = cursor.fetchone()
	return result[0] if result is not None else None

def getParticipantsByEventId(eventId):
	cursor.execute(
		"""
			select u.username from usersEvents ue
			join users u on ue.userId = u.id
			where ue.eventId = %s
		""", (eventId,)
	)
	result = cursor.fetchall()
	return result if result is not None else []

def getEventsByUserId(userId):
	cursor.execute(
		"""
			select
			e.id, e.name, e.description, (
				select name from venues where id = e.venue
			), e.datetime
			from usersEvents ue
			join events e on ue.eventId = e.id
			where ue.userId = %s
		""", (userId,)
	)
	results = cursor.fetchall()
	EventRecord = namedtuple("EventRecord", "id, name, description, venue, datetime")
	eventMap = map(EventRecord._make, results)
	events = []

	for event in eventMap:
		e = {
			"id": event.id,
			"name": event.name,
			"description": event.description.decode("utf-8"),
			"venue": event.venue,
			"datetime": event.datetime
		}
		events.append(e)

	return events