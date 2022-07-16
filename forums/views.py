from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from bson.json_util import loads, dumps
import json
from bson.objectid import ObjectId
import uuid;

import pymongo
my_client = pymongo.MongoClient('mongodb+srv://readherring:readherring@readherring.qlngl1v.mongodb.net/?retryWrites=true&w=majority')

db = my_client['readherring']

collection_name = db['Forums']

collection_name.drop({})
#let's create two documents
thread1 = {
    "title": "first title",
    "username": "user 1",
    "first_message": "message 1"
}
thread2 = {
    "title": "second title",
    "username": "user 2",
    "first_message": "message 2"
}

collection_name.insert_many([thread1, thread2])

# Create your views here.
def get_create_threads(request):
    if request.method == 'GET':
        thread_list = []
        data = collection_name.find({})
        for thread in data:
            thread['id'] = str(thread['_id'])
            thread.pop('_id', None)
            thread_list.append(thread)
        return JsonResponse(thread_list, safe=False)
    elif request.method == 'POST':
        data = request.body.decode('utf-8')
        json_data = json.loads(data)
        title = json_data['title']
        username = json_data['username']
        first_message = json_data['first_message']
        collection_name.insert_one({"title": title,"username": username,"first_message": first_message})
        return HttpResponse('New Thread Created!')
    else:
        print('error')

def get_by_id(request, id):
    # id_string = str(id)
    if request.method == 'GET':
        data = collection_name.find({"_id": ObjectId(id)})
        book = data[0]
        book['id'] = str(book['_id'])
        book.pop('_id', None)
        return JsonResponse(book, safe=False)
    elif request.method == 'PATCH':
        data = request.body.decode('utf-8')
        json_data = json.loads(data)

        if json_data['method'] == 'thread_message':
            username = json_data['username']
            message = json_data['message']
            message_id = str(uuid.uuid4())
            print(message_id)
            collection_name.update_one({'_id': ObjectId(id)},{'$push':{'messages': {'message_id': message_id, 'username': username, 'message': message, 'replies': [] }}}, upsert=True)
            return HttpResponse('New Message Added To Thread!')
        elif json_data['method'] == 'reply_message':
            message_id = json_data['message_id']
            username = json_data['username']
            reply = json_data['reply']
            reply_to = json_data['reply_to']
            collection_name.update_one({'_id': ObjectId(id), "messages.message_id": message_id} ,{'$push':{'messages.$.replies': {'username': username, 'reply': reply, 'reply_to': reply_to}}}, upsert=True)
            return HttpResponse('New Reply To Message in Thread!')


