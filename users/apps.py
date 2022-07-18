from django.apps import AppConfig
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
from django.contrib.auth.models import User
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.conf import settings

import json





# login route
def user_login(request):
    # gets response from FE
    user_information = json.loads(request.body)
    email = user_information['email']
    password = user_information['password']
    username = User.objects.get(email=email.lower()).username
    # authenticate user
    user = authenticate(request, username=username, password=password)
    # check user exists
    if user is not None:
        login(request, user)
        return JsonResponse({'message': 'login successful'})
    else:
        return JsonResponse({'error': 'login unsuccessful'})


# logout route
def user_logout(request):
    # to be deleted when we can log in
    user1 = authenticate(request, username='will', password='will')
    if user1 is not None:
        login(request, user1)
    #########
    logout(request)
    return JsonResponse({'message': 'User logged out'})


# create a new user route
def new_user(request):
    # get information from FE
    user_information = json.loads(request.body)
    # create user with data
    User.objects.create_user(
        username=user_information['name'], email=user_information['email'], password=user_information['password'])
    return JsonResponse({'message': 'user successfully created'})

