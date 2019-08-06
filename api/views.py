from django.shortcuts import render
from django.http import JsonResponse
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()
"""
db = pymysql.connect(
    os.getenv("DB_HOST"),
    os.getenv("DB_USER"),
    os.getenv("DB_PASS"),
    os.getenv("DB_NAME")
)
cursor = db.cursor()
"""
# Create your views here.
def homePage(request):
    return render(request, 'home.html')

def getUsers(request):
    cursor.execute("select * from users")
    users = cursor.fetchall()

    return JsonResponse({ "data": users })

def getEvents(request):
    cursor.execute("select * from events")
    events = cursor.fetchall()

    return JsonResponse({ "data": events })