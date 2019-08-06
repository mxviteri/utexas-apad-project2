from django.http import JsonResponse
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

db = pymysql.connect(
    os.getenv("DB_HOST"),
    os.getenv("DB_USER"),
    os.getenv("DB_PASS"),
    os.getenv("DB_NAME")
)
cursor = db.cursor()

def getUsers(request):
    cursor.execute("select * from users")
    users = cursor.fetchall()

    return JsonResponse({ "data": users })

def getEvents(request):
    cursor.execute("select * from events")
    events = cursor.fetchall()

    return JsonResponse({ "data": events })


def isAdmin(name):
	cursor.execute(
		"""
		SELECT name
		FROM roles
		JOIN users
		ON roles.id = users.role
		WHERE users.user = ?
		""",
		(name,)
	)
	result = cursor.fetchone()
	return True if result != None and result[0] == "admin" else False

# def findUser(name):
#     cursor.execute("select * from users where user = ?", (name,))
#     result = cursor.fetchone()
#     return None
    # if result:
    #     UserRecord = namedtuple("UserRecord", "id, name, role, event")
    #     user = UserRecord._make(result)	
    #     return user
    # else:
    #     return None