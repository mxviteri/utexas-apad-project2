from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
import api.controllers as controllers
import json

#### TEMPLATES ####
def homePage(request):
    return render(request, 'home.html')

def events(request):
    events = controllers.getEvents()

    if request.method == "POST":
        searchTerm = request.POST["search"]

        if searchTerm:
            events = list(filter(lambda e: e.name == searchTerm, events))

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

def create_account(request):
    return render(request, 'create_account.html')

#### PAGE ACTIONS / REDIRECTS ####

def handleLogin(request):
    response = HttpResponseRedirect('/events')
    password, username = sorted(list(request.POST.values()))
    result = controllers.loginUser(username, password)

    if len(result) > 0:
        response.set_cookie('user', result)
    else:
        response = HttpResponseRedirect('/')
        response.set_cookie('user', {})

    return response

def handleLogout(request):
    response = HttpResponseRedirect('/')
    response.set_cookie('user', {})
    return response

def handleCreateAccount(request):
    try:
        password, username = sorted(list(request.POST.values()))
        controllers.addUser(username, password, 'user')
    except Exception as e:
        context = { 'warning': 'Could not create account. Try again' }
        return render(request, 'create_account.html', context)
    
    response = HttpResponseRedirect('/')
    return response

def handleJoinEvent(request):
    response = HttpResponseRedirect('/')

#### REQUEST HANDLERS ####
@require_http_methods(["GET"])
def getUsers(request):
	users = controllers.getUsers()
	return JsonResponse({ "data": users })


@require_http_methods(["GET"])
def getEvents(request):
    eventsTuple = controllers.getEvents()
    events = []

    for event in eventsTuple:
	    e = {
			"id": event.id,
			"name": event.name,
			"venue": event.venue,
			"datetime": event.datetime,
            "capacity": event.capacity,
            "description": event.description
		}
	    events.append(e)


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