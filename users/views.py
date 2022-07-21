from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
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

from users.seeds import user1, user2
# collection_name.drop({})
# collection_name.insert_many([user1, user2])


# Create your views here.
def get_users(request):
    if request.method == 'GET':
        try:
            user_list = []
            data = collection_name.find({})
            for user in data:
                user['id'] = str(user['_id'])
                user.pop('_id', None)
                user.pop('password', None)
                user_list.append(user)
            return JsonResponse(user_list, safe=False)
        except TypeError:
            return HttpResponseNotFound('Could not find any users in the database')
    else:
        return HttpResponseBadRequest('Only GET requests allowed')

def get_by_username(request, username):
    if request.method == 'GET':
        try:
            user = collection_name.find_one({"username": username})
            user['id'] = str(user['_id'])
            user.pop('_id', None)
            user.pop('password', None)
            return JsonResponse(user, safe=False, status=200)
        except TypeError:
            response = {'error': f'Could not find user with username: {username} in database'}
            return JsonResponse(response, safe=False, status=200) # 200 as returning this error to display

    elif request.method == 'PATCH':
        data = request.body.decode('utf-8')
        json_data = json.loads(data)

        if json_data['method'] == 'add_to_read':
            ISBN = json_data['ISBN']
            title = json_data['title']
            author = json_data['author']
            has_read_data = {'ISBN': ISBN, 'title': title, 'author': author, 'favourited': False,
            'personal_rating': 0
            }
            collection_name.update_one({'username': username},{'$push':{'has_read': has_read_data}}, upsert=True)
            collection_name.update_one({'username': username}, {'$pull': { 'wants_to_read' : { 'ISBN': ISBN}}})
            return JsonResponse(has_read_data, status=200)
        elif json_data['method'] == 'remove_from_read':
            ISBN = json_data['ISBN']
            collection_name.update_one({'username': username}, {'$pull': { "has_read" : { 'ISBN': ISBN}}})
            return HttpResponse(status=204)
        elif json_data['method'] == 'edit_favourite_status':
            ISBN = json_data['ISBN']
            set_favourited = json_data['set_favourited']
            collection_name.update_one({'username': username, "has_read.ISBN": ISBN} ,{'$set':{'has_read.$.favourited': set_favourited}}, upsert=True)
            return HttpResponse(status=204)
        elif json_data['method'] == 'add_to_wants_to_read':
            ISBN = json_data['ISBN']
            title = json_data['title']
            author = json_data['author']
            wants_to_read_data = {'ISBN': ISBN, 'title': title, 'author': author}
            collection_name.update_one({'username': username},{'$push': {'wants_to_read': wants_to_read_data}}, upsert=True)
            return JsonResponse(wants_to_read_data, status=200)
        elif json_data['method'] == 'remove_from_wants_to_read':
            ISBN = json_data['ISBN']
            collection_name.update_one({'username': username}, {'$pull': { 'wants_to_read': { 'ISBN': ISBN}}})
            return HttpResponse(status=204)
        elif json_data['method'] == 'edit_about_me':
            about_me = json_data['about_me']
            collection_name.update_one({'username': username} ,{'$set':{'about_me': about_me}}, upsert=True)
            return HttpResponse(status=204)
        elif json_data['method'] == 'add_to_following':
            user_to_follow = json_data['user_to_follow']
            add_not_take = json_data['add_not_take']
            if add_not_take == True:
                collection_name.update_one({'username': username},{'$push': {'following': user_to_follow}}, upsert=True)
            elif add_not_take == False:
                collection_name.update_one({'username': username},{'$pull': {'following': user_to_follow}}, upsert=True)
            else:
                return HttpResponseBadRequest('Check request Body')
            data = collection_name.find_one({'username': username})
            following_array = data['following']
            return JsonResponse(following_array, safe=False, status=200)

    else:
        return HttpResponseBadRequest('Only GET and PATCH requests allowed')


def register(request):
    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    username = json_data['username']
    email = json_data['email']
    username_exists = collection_name.find_one({'username': username}, {"username" : 1});
    email_exists = collection_name.find_one({'email': email}, {"email" : 1});
    if username_exists != None:
        response = {'error': f'A user already exists with username {username}'}
        return JsonResponse(response, safe=False, status=409)
    elif email_exists != None:
        response = {'error': f'A user already exists with email {email}'}
        return JsonResponse(response, safe=False, status=409)
    else:
        password = json_data['password']
        hashed_password = make_password(password)
        about_me = "This is where I can write a little something about myself!"
        collection_name.insert_one({'username': username, 'password': hashed_password, 'email': email, 'about_me': about_me, 'has_read':[], 'wants_to_read':[], 'following':[]})
        response = {'msg': 'You have successfully created a new account. Try to Login!'}
        return JsonResponse(response, safe=False, status=201)

def login(request):
    data = request.body.decode('utf-8')
    json_data = json.loads(data)
    user_input = json_data['user_input']
    password = json_data['password']
    db_data = collection_name.find_one({"username": user_input})
    if db_data == None:
        db_data = collection_name.find_one({"email": user_input})
        if db_data == None:
            response = {'error': 'An account with that username / email could not be found'}
            return JsonResponse(response, safe=False, status=401)
    else:
        db_password = db_data['password']
        check = check_password(password, db_password)
        db_data['id'] = str(db_data['_id'])
        db_data.pop('_id', None)
        if check == True:
            db_data.pop('password', None)
            return JsonResponse(db_data, safe=False, status=200)
        else:
            response = {'error': 'Incorrect Password'}
            return JsonResponse(response, safe=False, status=401)


def not_found_404(request, exception):
    response = {'error': exception}
    return JsonResponse(response, safe=False)


def server_error_500(request):
    response = {'error': '500 Error'}
    return JsonResponse(response, safe=False)

