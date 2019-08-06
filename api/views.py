from django.shortcuts import render
from django.http import JsonResponse
import api.controllers as controllers

# Create your views here.
def homePage(request):
    return render(request, 'home.html')

#### REQUEST HANDLERS ####
def getUsers(request):
	users = controllers.getUsers()
	return JsonResponse({ "data": users })

def getEvents(request):
    events = controllers.getEvents()
    return JsonResponse({ "data": events })