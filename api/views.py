from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import api.controllers as controllers
import json

#### TEMPLATES ####
def homePage(request):
    return render(request, 'home.html')

def events(request):
    events = controllers.getEvents()  
    context = {
        'events': events
    }
    return render(request, 'events.html', context)

def event_detail(request, eventId):
    event = controllers.getEvent(eventId)
    context = {
        'event': event
    }
    return render(request, 'event_detail.html', context)

#### REQUEST HANDLERS ####
@require_http_methods(["GET"])
def getUsers(request):
	users = controllers.getUsers()
	return JsonResponse({ "data": users })


@require_http_methods(["GET"])
def getEvents(request):
    events = controllers.getEvents()
    return JsonResponse({ "data": events })


@require_http_methods(["POST"])
def addUser(request):
    body = json.loads(request.body)
    username = body["username"]
    password = body["password"]
    role = "admin" if body["isAdmin"] else "user"

    try:
        result = controllers.addUser(username, password, role)
        return JsonResponse({ "msg": result })
    except Exception as e:
        return JsonResponse({ "msg": str(e) }, status=400)


@require_http_methods(["POST"])
def loginUser(request):
    body = json.loads(request.body)
    username = body["username"]
    password = body["password"]

    try:
        result = controllers.loginUser(username, password)
        if len(result) == 0:
            return JsonResponse({ "msg": "No user found" }, status=404)

        return JsonResponse({ "msg": "User logged in successfully", "user": result })
    except Exception as e:
        return JsonResponse({ "msg": str(e) }, status=400)


@require_http_methods(["POST"])
def joinEvent(request, eventId):
    body = json.loads(request.body)
    userId = body["userId"]

    try:
        result = controllers.joinEvent(userId, eventId)
        return JsonResponse({ "msg": result })
    except Exception as e:
        return JsonResponse({ "msg": str(e) }, status=400)


@require_http_methods(["GET"])
def getEventCapacity(request, eventId):
    try:
        result = controllers.getCapacityByEventId(eventId)
        if not result:
            return JsonResponse({ "msg": "No event found" }, status=404)

        return JsonResponse({ "capacity": result })
    except Exception as e:
        return JsonResponse({ "msg": str(e) }, status=400)


@require_http_methods(["GET"])
def getEventParticipants(request, eventId):
    try:
        result = controllers.getParticipantsByEventId(eventId)
        return JsonResponse({ "participants": result })
    except Exception as e:
        return JsonResponse({ "msg": str(e) }, status=400)


@require_http_methods(["GET"])
def getUserEvents(request, userId):
    try:
        result = controllers.getEventsByUserId(userId)
        return JsonResponse({ "events": result })
    except Exception as e:
        return JsonResponse({ "msg": str(e) }, status=400)