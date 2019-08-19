"""project2 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
import api.views as views

# deploying changes
urlpatterns = [
    ## PAGE ROUTES ##
    path('', views.homePage),
    path('events/', views.events),
    path('events/<int:eventId>', views.event_detail),
    path('myevents/', views.my_events),
    path('create_account/', views.create_account),
    ## ADMIN ##
    path('admin/', views.admin, name="admin"),
    ## PAGE ACTIONS ###
    path('action/login', views.handleLogin),
    path('action/logout', views.handleLogout),
    path('action/create_account', views.handleCreateAccount),
    path('action/join_event/<int:eventId>', views.handleJoinEvent),
    path('action/leave_event/<int:eventId>', views.handleLeaveEvent),
    path('action/create_event', views.handleCreateEvent),
    path('action/delete_user', views.handleUserDelete),
    path('action/delete_event', views.handleEventDelete),
    path('action/create_venue', views.handleCreateVenue),
    path('action/delete_venue', views.handleVenueDelete),
    ## API ROUTES ##
    path('api/users', views.addUser),
    path('api/users/all', views.getUsers),
    path('api/users/login', views.loginUser),
    path('api/users/delete', views.deleteUser),
    path('api/users/<int:userId>/events', views.getUserEvents),
    path('api/events', views.getEvents),
    path('api/events/join', views.joinEventRequest),
    path('api/events/leave', views.leaveEventRequest),
    path('api/events/<int:eventId>', views.handleEvents),
    path('api/events/<int:eventId>/capacity', views.getEventCapacity),
    path('api/events/<int:eventId>/participants', views.getEventParticipants),
    path('api/venues', views.getVenues),
    path('api/events/create', views.createEvent)
]
