from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.
def testing(request):
    return JsonResponse({ "msg": "welcome" })