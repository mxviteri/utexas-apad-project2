import pymysql
from dotenv import load_dotenv
import os
from collections import namedtuple

load_dotenv()

def dbConnect():
	return pymysql.connect(
		os.getenv("DB_HOST"),
		os.getenv("DB_USER"),
		os.getenv("DB_PASS"),
		os.getenv("DB_NAME")
	)

def getUsers():
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute("select id, username, role from users")
	result = cursor.fetchall()
	cursor.close()
	UserRecord = namedtuple("UserRecord", "id, username, role")
	users = map(UserRecord._make, result)
	return list(users)

def getEvents():
	events = []
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute("select e.id, e.name, v.name, e.datetime, e.capacity, convert(e.description using utf8) from events e join venues v on e.venue=v.id")
	result = cursor.fetchall()
	cursor.close()
	for item in result:
		EventRecord = namedtuple("EventRecord", "id, name, venue, datetime, capacity, description")
		event = EventRecord._make(item)
		events.append(event)
	return events

def searchEvents(query):
	events = []
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute("""select e.id, e.name, v.name, e.datetime, e.capacity, convert(e.description using utf8) from events e join venues v on e.venue=v.id where e.name COLLATE UTF8_GENERAL_CI like 
	"%\%s%" """, (query,))
	result = cursor.fetchall()
	cursor.close()
	for item in result:
		EventRecord = namedtuple("EventRecord", "id, name, venue, datetime, capacity, description")
		event = EventRecord._make(item)
		events.append(event)
	return events

def getVenues():
	venues = []
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute("select id, name, open, close from venues")
	results = cursor.fetchall()
	cursor.close()
	for r in results:
		venue = {
			"id": r[0],
			"name": r[1],
			"open": r[2],
			"close": r[3]
		}
		venues.append(venue)
	return venues

def createVenue(name, venueOpen, venueClose):
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute(
		"insert into venues(name, open, close) values(%s, %s, %s)",
		(name, venueOpen, venueClose)
	)
	rows = cursor.rowcount

	if not rows == 1:
		db.rollback()
		raise Exception('Venue not added')

	db.commit()
	cursor.close()
	msg = "Venue {} has been added successfully".format(name)
	return msg

def deleteVenue(venueId):
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute(
		"delete from venues where id = %s", (venueId,)
	)
	rows = cursor.rowcount
	
	if not rows == 1:
		db.rollback()
		raise Exception('Venue not deleted')

	db.commit()
	cursor.close()
	msg = "Venue {} has been deleted successfully".format(venueId)
	return msg

def getEvent(eventId):
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute("select e.id, e.name, v.name, e.datetime, e.capacity, convert(e.description using utf8) from events e join venues v on e.venue = v.id where %s = e.id", (eventId,))
	result = cursor.fetchone()
	EventRecord = namedtuple("EventRecord", "id, name, venue, datetime, capacity, description")
	event = EventRecord._make(result)
	return event

def isAdmin(name):
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute(
		"""
		select name from roles
		join users on roles.id = users.role
		where users.user = %s
		""", (name,)
	)
	result = cursor.fetchone()
	cursor.close()
	return True if result and result[0] == "admin" else False

def findUser(name):
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute("select * from users where user = %s", (name,))
	result = cursor.fetchone()
	cursor.close()
	return result[1] if result else None

def addUser(username, password, role):
	db = dbConnect()
	cursor = db.cursor()
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
	cursor.close()
	msg = "User {} has been added successfully".format(username)
	return msg

def deleteUser(userId):
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute(
		"delete from users where id = %s", (userId,)
	)
	rows = cursor.rowcount
	
	if not rows == 1:
		db.rollback()
		raise Exception('User not deleted')

	db.commit()
	cursor.close()
	msg = "User {} has been deleted successfully".format(userId)
	return msg

def loginUser(username, password):
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute(
		"""
		select u.id, u.username, r.name from users u
		join roles r on u.role = r.id
		where username = %s and password = %s
		""", (username, password)
	)
	result = cursor.fetchone()
	cursor.close()
	if not result:
		return {}

	return {
		"id": result[0],
		"username": result[1],
		"role": result[2]
	}

def joinEvent(userId, eventId):
	(total, capacity) = currentParticipantTotal(eventId)

	if total >= capacity:
		raise Exception('The event with id: {}, is at capacity'.format(eventId))

	db = dbConnect()
	cursor = db.cursor()	
	cursor.execute(
		"insert into usersEvents(userId, eventId) values(%s, %s)", (userId, eventId)
	)

	rows = cursor.rowcount
	if not rows == 1:
		db.rollback()
		raise Exception('User could not join event')

	db.commit()
	cursor.close()
	msg = "User has successfully joined the event"
	return msg

def leaveEvent(userId, eventId):
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute(
		"delete from usersEvents where userId = %s and eventId = %s", (userId, eventId)
	)

	rows = cursor.rowcount
	if not rows == 1:
		db.rollback()
		raise Exception('User could not leave event')

	db.commit()
	cursor.close()
	msg = "User has left the event"
	return msg

def getCapacityByEventId(eventId):
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute("select capacity from events where id = %s", (eventId,))
	result = cursor.fetchone()
	cursor.close()
	return result[0] if result is not None else None

def getParticipantsByEventId(eventId):
	users = []
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute(
		"""
			select u.username from usersEvents ue
			join users u on ue.userId = u.id
			where ue.eventId = %s
		""", (eventId,)
	)
	result = cursor.fetchall()
	cursor.close()
	if result:
		for item in result:
			users.append(item[0])
	return users

def getEventsByUserId(userId):
	db = dbConnect()
	cursor = db.cursor()
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
	cursor.close()
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

def currentParticipantTotal(eventId):
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute(
		"""
			SELECT COUNT(ue.userId) as total, e.capacity
			FROM events e
			LEFT JOIN usersEvents ue on e.id = ue.eventId
			WHERE e.id = %s
			GROUP BY ue.eventId
		""", (eventId,)
	)
	TotalRecord = namedtuple('TotalRecord','total, capacity')
	result = cursor.fetchone()
	cursor.close()

	if not result:
		raise Exception('The event with id: {}, could not be found'.format(eventId))

	record = TotalRecord._make(result)
	return (record.total, record.capacity)

def createEvent(name, description, venueId, datetime, capacity):
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute(
		"""insert into events(name, description, venue, datetime, capacity) values(%s, %s, %s, %s, %s)""",
		(name, description, venueId, datetime, capacity))
	rows = cursor.rowcount

	if not rows == 1:
		db.rollback()
		raise Exception('Event not created')

	db.commit()
	cursor.close()
	msg = "Event {} has been added successfully".format(name)
	return msg

def deleteEvent(eventId):
	db = dbConnect()
	cursor = db.cursor()
	cursor.execute(
		"""delete from events where id = %s""",
		(eventId,))
	rows = cursor.rowcount

	if not rows == 1:
		db.rollback()
		raise Exception('Event not deleted')

	db.commit()
	cursor.close()
	msg = "Event has been successfully deleted"
	return msg