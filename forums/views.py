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

thread1 = {
    "title": "Hello Chris! This is the title of a thread",
    "username": "Aaron, the creator of this thread",
    "first_message": "The first main message that starts the thread off goes here. Let me know if anything needs to be restructured to make it easier to display/ function, or if you want to display it a different way!",
    "messages": [{"message_id": "id I will generate for you to be referenced in replies", "username": "user who sent this message", "message": "Whatever could this be?",
    "replies": [
        {
        "username": "user who sent this reply",
        "reply": "The first reply to this message",
        "reply_to": "Is this a reply to another user who has replied or is it just a reply to the original message in which case ''"
        },
        {
        "username": "user",
        "reply": "The second reply to this message",
        "reply_to": ""
        }
    ]},
    {"message_id": '12345', "username": "user1", "message": "user1 has sent another message to view in the thread",
    "replies": [
        {
        "username": "user2",
        "reply": "user2 has sent this reply to the main message from user1",
        "reply_to": ""
        },
        {
        "username": "user3",
        "reply": "user3 has also sent this reply to the main message",
        "reply_to": ""
        },
        {
        "username": "user1",
        "reply": "user1 has replied to user2's message",
        "reply_to": "user2"
        },
        {
        "username": "user4",
        "reply": "user4 has replied to user3's message",
        "reply_to": "user3"
        },
        {
        "username": "user5",
        "reply": "user5 has sent another reply to the original message not targeted at anyone",
        "reply_to": ""
        }
        
    ]}
    ]
}
thread2 = {
    "title": "A second thread",
    "username": "user1",
    "first_message": "What an original message this is",
    "messages": [{"message_id": '11111', "username": "user2", "message": "This is message 1",
    "replies": [
        {
        "username": "user3",
        "reply": "The first reply to message 1",
        "reply_to": ""
        },
        {
        "username": "user4",
        "reply": "The second reply to message 1",
        "reply_to": ""
        }
    ]},
    {"message_id": '22222', "username": "user5", "message": "This is message 2",
    "replies": [
        {
        "username": "user1",
        "reply": "The first reply to message 2",
        "reply_to": ""
        },
        {
        "username": "user3",
        "reply": "The second reply to message 2 which is also a reply to user1",
        "reply_to": "user1"
        },
        {
        "username": "user5",
        "reply": "Third reply to message 2",
        "reply_to": ""
        }
    ]}
    ]
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
        thread = collection_name.find_one({"_id": ObjectId(id)})
        if thread == None:
            return HttpResponse(f'Could not find thread with id: {id}')
        else:
            thread['id'] = str(thread['_id'])
            thread.pop('_id', None)
            return JsonResponse(thread, safe=False)
    elif request.method == 'PATCH':
        data = request.body.decode('utf-8')
        json_data = json.loads(data)

        if json_data['method'] == 'thread_message':
            username = json_data['username']
            message = json_data['message']
            message_id = str(uuid.uuid4())
            collection_name.update_one({'_id': ObjectId(id)},{'$push':{'messages': {'message_id': message_id, 'username': username, 'message': message, 'replies': [] }}}, upsert=True)
            return HttpResponse('New Message Added To Thread!')
        elif json_data['method'] == 'reply_message':
            message_id = json_data['message_id']
            username = json_data['username']
            reply = json_data['reply']
            reply_to = json_data['reply_to']
            collection_name.update_one({'_id': ObjectId(id), "messages.message_id": message_id} ,{'$push':{'messages.$.replies': {'username': username, 'reply': reply, 'reply_to': reply_to}}}, upsert=True)
            return HttpResponse('New Reply To Message in Thread!')


def not_found_404(request, exception):
    response = {'error': exception}
    return JsonResponse(response, safe=False)


def server_error_500(request):
    response = {'error': '500 Error'}
    return JsonResponse(response, safe=False)

