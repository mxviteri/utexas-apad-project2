from django.shortcuts import render
from django.http import JsonResponse
import api.controllers as controllers
import json

# Create your views here.
def homePage(request):
    events = controllers.getEvents()  
    context = {
        'events': events
    }
    return render(request, 'home.html', context)

#### REQUEST HANDLERS ####
def getUsers(request):
	users = controllers.getUsers()
	return JsonResponse({ "data": users })

def getEvents(request):
    events = controllers.getEvents()
    return JsonResponse({ "data": events })

def postUser(request):
    body = json.loads(request.body)
    name = body["name"]
    role = body["role"]
    user = body["user"]

    try:
        result = controllers.addUser(name, role, user)
        return JsonResponse({ "msg": result })
    except Exception as e:
        return JsonResponse({ "msg": str(e) }, status=400)

