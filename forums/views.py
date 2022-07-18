from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from bson.json_util import loads, dumps
import json
from bson.objectid import ObjectId
import uuid;
import pymongo

# For refreshing server to seed data
from forums.seeds import thread1, thread2
# collection_name.drop({})
# collection_name.insert_many([thread1, thread2])



my_client = pymongo.MongoClient('mongodb+srv://readherring:readherring@readherring.qlngl1v.mongodb.net/?retryWrites=true&w=majority')

db = my_client['readherring']

collection_name = db['Forums']




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
            reply_data = {'username': username, 'reply': reply, 'reply_to': reply_to}
            collection_name.update_one({'_id': ObjectId(id), "messages.message_id": message_id} ,{'$push':{'messages.$.replies': reply_data}}, upsert=True)
            return JsonResponse(reply_data, safe=False)


def not_found_404(request, exception):
    response = {'error': exception}
    return JsonResponse(response, safe=False)


def server_error_500(request):
    response = {'error': '500 Error'}
    return JsonResponse(response, safe=False)

