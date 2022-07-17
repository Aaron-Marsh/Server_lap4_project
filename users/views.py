from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from bson.json_util import loads, dumps
import json
from bson.objectid import ObjectId
import uuid;

import pymongo
my_client = pymongo.MongoClient('mongodb+srv://readherring:readherring@readherring.qlngl1v.mongodb.net/?retryWrites=true&w=majority')

db = my_client['readherring']

collection_name = db['Users']

collection_name.drop({})

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


