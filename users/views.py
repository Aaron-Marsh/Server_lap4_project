from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from bson.json_util import loads, dumps
from bson.objectid import ObjectId
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core import serializers
from django.core.mail import send_mail
from django.conf import settings
import json
import uuid

from django.contrib.auth.hashers import make_password, check_password



import pymongo
my_client = pymongo.MongoClient('mongodb+srv://readherring:readherring@readherring.qlngl1v.mongodb.net/?retryWrites=true&w=majority')

db = my_client['readherring']

collection_name = db['Users']

collection_name.drop({})


# login route


user1 = {
    'username': 'user1',
    'password': 'pass'
}
user2 = {
    'username': 'user2',
    'password': 'pass'
}

collection_name.insert_many([user1, user2])

# Create your views here.
def get_users(request):
    if request.method == 'GET':
        user_list = []
        data = collection_name.find({})
        for user in data:
            user['id'] = str(user['_id'])
            user.pop('_id', None)
            user_list.append(user)
        return JsonResponse(user_list, safe=False)
    # elif request.method == 'POST':
    #     data = request.body.decode('utf-8')
    #     json_data = json.loads(data)
    #     title = json_data['title']
    #     username = json_data['username']
    #     first_message = json_data['first_message']
    #     collection_name.insert_one({"title": title,"username": username,"first_message": first_message})
    #     return HttpResponse('New Thread Created!')
    else:
        print('error')

def get_by_username(request, username):
    # id_string = str(id)
    if request.method == 'GET':
        user = collection_name.find_one({"username": username})
        user['id'] = str(user['_id'])
        user.pop('_id', None)
        return JsonResponse(user, safe=False)
    elif request.method == 'PATCH':
        data = request.body.decode('utf-8')
        json_data = json.loads(data)

        if json_data['method'] == 'add_to_read':
            ISBN = json_data['ISBN']
            title = json_data['title']
            author = json_data['author']
            collection_name.update_one({'username': username},{'$push':{'has_read': {'ISBN': ISBN, 'title': title, 'author': author, 'favourited': False, 'personal_rating': 0 }}}, upsert=True)
            return HttpResponse(f'New book with ISBN: {ISBN} added to read for {username}!')
        elif json_data['method'] == 'edit_favourite_status':
            ISBN = json_data['ISBN']
            set_favourited = json_data['set_favourited']
            collection_name.update_one({'username': username, "has_read.ISBN": ISBN} ,{'$set':{'has_read.$.favourited': set_favourited}}, upsert=True)
            return HttpResponse(f'Book with ISBN: {ISBN} has favourite status set to {set_favourited} for {username}!')


def register(request):
    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    username = json_data['username']
    email = json_data['email']
    username_exists = collection_name.find_one({'username': username}, {"username" : 1});
    email_exists = collection_name.find_one({'email': email}, {"email" : 1});
    if username_exists != None:
        response = {'error': f'A user already exists with username {username}'}
        return JsonResponse(response, safe=False)
    elif email_exists != None:
        response = {'error': f'A user already exists with email {email}'}
        return JsonResponse(response, safe=False)
    else:
        password = json_data['password']
        hashed_password = make_password(password)
        collection_name.insert_one({'username': username, 'password': hashed_password, 'email': email})
        response = {'msg': 'You have successfully created a new account. Try to Login!'}
        return JsonResponse(response, safe=False)

def login(request):
    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    user_input = json_data['userInput']
    password = json_data['password']
    db_data = collection_name.find_one({"username": user_input})
    if db_data == None:
        db_data = collection_name.find_one({"email": user_input})
        if db_data == None:
            response = {'error': 'An account with that username / email could not be found'}
            return JsonResponse(response, safe=False)
    db_password = db_data['password']
    check = check_password(password, db_password)
    db_data['id'] = str(db_data['_id'])
    db_data.pop('_id', None)
    if check == True:
        db_data.pop('password', None)
        return JsonResponse(db_data, safe=False)
    else:
        response = {'error': 'Incorrect Password'}
        return JsonResponse(response, safe=False)


# def user_login(request):
#     # gets response from FE
#     user_information = json.loads(request.body)
#     email = user_information['email']
#     password = user_information['password']
#     username = User.objects.get(email=email.lower()).username
#     # authenticate user
#     user = authenticate(request, username=username, password=password)
#     # check user exists
#     if user is not None:
#         login(request, user)
#         return JsonResponse({'message': 'login successful'})
#     else:
#         return JsonResponse({'error': 'login unsuccessful'})


# # logout route
# def user_logout(request):
#     # to be deleted when we can log in
#     user1 = authenticate(request, username='will', password='will')
#     if user1 is not None:
#         login(request, user1)
#     #########
#     logout(request)
#     return JsonResponse({'message': 'User logged out'})


# # create a new user route
# def new_user(request):
#     # get information from FE
#     # user_information = json.loads(request.body)
#     user_information = {
#         'name': 'William',
#         'email': 'w@g.com',
#         'password': 'password',
#     }
#     # create user with data
#     User.objects.create_user(
#         username=user_information['name'], email=user_information['email'], password=user_information['password'])
#     return JsonResponse({'message': 'user successfully created'})


