from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from bson.json_util import loads, dumps
import json
from bson.objectid import ObjectId
import uuid;
import pymongo

# For refreshing server to seed data
from forums.seeds import thread1, thread2



my_client = pymongo.MongoClient('mongodb+srv://readherring:readherring@readherring.qlngl1v.mongodb.net/?retryWrites=true&w=majority')

db = my_client['readherring']

collection_name = db['Forums']
collection_name.create_index([('title', 'text')], default_language='english')
# collection_name.drop({})
# collection_name.insert_many([thread1, thread2])



# Create your views here.
def get_threads(request):
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
        add_thread = collection_name.insert_one({'title': title, 'username': username, 'firstmessage': first_message })
        thread_data = {'id': str(add_thread.inserted_id), 'title': title, 'username': username, 'firstmessage': first_message }
        return JsonResponse(thread_data, safe=False)
    else:
        print('error')

def get_by_id(request, id):
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
            message_id = json_data.get('message_id', None)
            if message_id == None:
                message_id = str(uuid.uuid4())
                message_data = {'message_id': message_id, 'username': username, 'message': message, 'replies': [] }
                collection_name.update_one({'_id': ObjectId(id)},{'$push':{'messages': message_data}}, upsert=True)
                return JsonResponse(message_data, safe=False)
            else:
                message_data = {'message_id': message_id, 'username': username, 'message': message, 'replies': [] }
                collection_name.update_one({'_id': ObjectId(id), 'messages.message_id': message_id},{'$set':{'messages.$.message': message}})
                return JsonResponse(message_data, safe=False)

        elif json_data['method'] == 'reply_message':
            message_id = json_data['message_id']
            username = json_data['username']
            reply = json_data['reply']
            reply_to = json_data['reply_to']
            reply_id = json_data.get('reply_id', None)
            if reply_id == None:
                reply_id = str(uuid.uuid4())
                reply_data = {'reply_id': reply_id, 'username': username, 'reply': reply, 'reply_to': reply_to}
                collection_name.update_one({'_id': ObjectId(id), 'messages.message_id': message_id} ,{'$push':{'messages.$.replies': reply_data}}, upsert=True)
                return JsonResponse(reply_data, safe=False)
            else:
                reply_data = {'reply_id': reply_id, 'username': username, 'reply': reply, 'reply_to': reply_to}
                data = collection_name.find_one({'messages.replies.reply_id': reply_id})
                messages = data['messages']
                for message in messages:
                    reply_was_changed = False
                    replies = message['replies']
                    edited_replies = []
                    for reply_object in replies:
                        if reply_object['reply_id'] == reply_id:
                            reply_object['reply'] = reply
                            reply_was_changed = True
                        edited_replies.append(reply_object)
                    if reply_was_changed == True:
                        collection_name.update_one({'_id': ObjectId(id), 'messages.message_id': message_id},{'$set':{'messages.$.replies': edited_replies}})
                return JsonResponse(reply_data, safe=False)

def search_by_title(request):
    if request.method == 'POST':
        data = request.body.decode('utf-8')
        json_data = json.loads(data)
        query = json_data['query']
        thread_list = []
        search = collection_name.find(
   { '$text': { '$search': query } })
        for thread in search:
            thread['id'] = str(thread['_id'])
            thread.pop('_id', None)
            thread_list.append(thread)
        return JsonResponse(thread_list, safe=False)

def not_found_404(request, exception):
    response = {'error': exception}
    return JsonResponse(response, safe=False)


def server_error_500(request):
    response = {'error': '500 Error'}
    return JsonResponse(response, safe=False)

