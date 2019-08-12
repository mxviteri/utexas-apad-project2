from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.http import require_http_methods
from datetime import datetime
import json

import api.controllers as controllers

#### TEMPLATES ####
def homePage(request):
    return render(request, 'home.html')

def events(request):
    events = controllers.getEvents()
    venues = controllers.getVenues()

    if request.method == "POST":
        searchTerm = request.POST["search"]

        if searchTerm:
            events = list(filter(lambda e: e.name == searchTerm, events))

    context = {
        'events': events,
        'venues': venues
    }
    return render(request, 'events.html', context)

def event_detail(request, eventId):
    event = controllers.getEvent(eventId)
    users = controllers.getParticipantsByEventId(eventId)
    context = {
        'event': event,
        'users': users
    }
    return render(request, 'event_detail.html', context)

def create_account(request):
    return render(request, 'create_account.html')

def my_events(request):
    user = request.USER
    if not user:
        return HttpResponseRedirect('/')

    userId = user["id"]
    events = controllers.getEventsByUserId(userId)
    upcoming = list(filter(lambda e: e["datetime"] >= datetime.now(), events))
    past = list(filter(lambda e: e["datetime"] < datetime.now(), events))
    eventDict = {
        "upcoming": upcoming,
        "past": past
    }

    return render(request, 'my_events.html', { "events": eventDict })

def admin(request):
    users = controllers.getUsers()
    venues = controllers.getVenues()
    events = controllers.getEvents()
    context = {
        "users": users,
        "venues": venues,
        "events": events
    }

    return render(request, 'admin.html', context)

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
    except:
        context = { 'warning': 'Could not create account. Try again.' }
        return render(request, 'create_account.html', context)
    
    response = HttpResponseRedirect('/')
    return response

def handleJoinEvent(request, eventId):
    try:
        controllers.joinEvent(userId=request.USER['id'], eventId=eventId)
    except:
        event = controllers.getEvent(eventId)
        users = controllers.getParticipantsByEventId(eventId)
        context = { 
            'warning': 'Could not join event.',
            'event': event,
            'users': users
            }
        return render(request, 'event_detail.html', context)
    return HttpResponseRedirect('/events/' + str(eventId))

def handleLeaveEvent(request, eventId):
    try:
        controllers.leaveEvent(userId=request.USER['id'], eventId=eventId)
    except:
        event = controllers.getEvent(eventId)
        users = controllers.getParticipantsByEventId(eventId)
        context = { 
            'warning': 'Could not leave event.',
            'event': event,
            'users': users
            }
        return render(request, 'event_detail.html', context)
    return HttpResponseRedirect('/events/' + str(eventId))

def handleCreateEvent(request):
    try:
        name = request.POST.get("name")
        description = request.POST.get("description")
        venueId = request.POST.get("venueId")
        datetime = request.POST.get("date")
        capacity = request.POST.get("capacity")
        controllers.createEvent(name, description, venueId, datetime, capacity)
    except:
        events = controllers.getEvents()
        venues = controllers.getVenues()
        context = { 
            'warning': 'Could not create event. Please try again.',
            'events': events,
            'venues': venues
            }
        return render(request, 'events.html', context)

    return HttpResponseRedirect('/events/')

def handleUserDelete(request):
    try:
        userId = request.POST.get("id")
        controllers.deleteUser(userId)
    except Exception as e:
        print(e)
    
    return HttpResponseRedirect('/admin/')

def handleEventDelete(request):
    try:
        eventId = request.POST.get("id")
        controllers.deleteEvent(eventId)
    except Exception as e:
        print(e)
    
    return HttpResponseRedirect('/admin/#events')
    

#### REQUEST HANDLERS ####
@require_http_methods(["GET"])
def getUsers(request):
	users = controllers.getUsers()
	return JsonResponse({ "data": users })

@require_http_methods(["DELETE"])
def deleteUser(request):
    try:
        body = json.loads(request.body)
        userId = body.get("id")
        msg = controllers.deleteUser(userId)
        return JsonResponse({ "msg": msg })
    except Exception as e:
        return JsonResponse({ "msg": e }, status=400)

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