from curses.ascii import HT
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
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
        try:
            thread_list = []
            data = collection_name.find({})
            for thread in data:
                thread['id'] = str(thread['_id'])
                thread.pop('_id', None)
                thread_list.append(thread)
            return JsonResponse(thread_list, safe=False, status=200)
        except TypeError:
            return HttpResponseNotFound('Could not find any threads in the database')

    elif request.method == 'POST':
        try:
            data = request.body.decode('utf-8')
            json_data = json.loads(data)
            title = json_data['title']
            username = json_data['username']
            first_message = json_data['first_message']
            add_thread = collection_name.insert_one({'title': title, 'username': username, 'first_message': first_message, 'likes': [] })
            thread_data = {'id': str(add_thread.inserted_id), 'title': title, 'username': username, 'first_message': first_message, 'likes': [] }
            return JsonResponse(thread_data, safe=False)
        except KeyError:
            return HttpResponseBadRequest('Invalid post, check request.body')
    else:
        return HttpResponseBadRequest('Only GET and POST requests allowed')

def get_by_id(request, id):
    if request.method == 'GET':
        try:
            thread = collection_name.find_one({"_id": ObjectId(id)})
            thread['id'] = str(thread['_id'])
            thread.pop('_id', None)
            return JsonResponse(thread, safe=False)
        except TypeError:
            return HttpResponseNotFound(f'Could not find thread with id: {id} in database')

    elif request.method == 'PATCH':
        data = request.body.decode('utf-8')
        json_data = json.loads(data)
        if json_data['method'] == 'edit_thread_title':
            title = json_data['title']
            collection_name.update_one({'_id': ObjectId(id)},{'$set':{'title': title}}, upsert=True)
            return HttpResponse(status=204)
        elif json_data['method'] == 'edit_thread_first_message':
            first_message = json_data['first_message']
            collection_name.update_one({'_id': ObjectId(id)},{'$set':{'first_message': first_message}}, upsert=True)
            return HttpResponse(status=204)
        # elif json_data['method'] == 'edit_likes':
        #     username = json_data['username']
        #     if json_data['like_not_unlike'] == True:
        #         collection_name.update_one({'_id': ObjectId(id)},{'$push':{'likes': username}}, upsert=True)
        #         return HttpResponse(status=204)
        #     elif json_data['like_not_unlike'] == False:
        #         collection_name.update_one({'_id': ObjectId(id)},{'$push':{'likes': username}}, upsert=True)
        #         return HttpResponse(status=204)
        #     else:
        #         return HttpResponseBadRequest('Check request body')
        elif json_data['method'] == 'thread_message':
            username = json_data['username']
            message = json_data['message']
            message_id = json_data.get('message_id', None)
            # For creating new message in thread
            if message_id == None:
                message_id = str(uuid.uuid4())
                message_data = {'message_id': message_id, 'username': username, 'message': message, 'replies': [] }
                collection_name.update_one({'_id': ObjectId(id)},{'$push':{'messages': message_data}}, upsert=True)
                return JsonResponse(message_data, safe=False, status=200)
            # For editing existing message in thread
            else:
                message_data = {'message_id': message_id, 'username': username, 'message': message, 'replies': [] }
                collection_name.update_one({'_id': ObjectId(id), 'messages.message_id': message_id},{'$set':{'messages.$.message': message}})
                return JsonResponse(message_data, safe=False, status=200)
    
        elif json_data['method'] == 'delete_message':
            try:
                message_id = json_data['message_id']
                collection_name.update_one({'_id': ObjectId(id)}, {'$pull': { "messages" : { 'message_id': message_id}}})
                return HttpResponse(status=204)
            except TypeError:
                return HttpResponseNotFound(f'Could not find message with message_id: {message_id} to delete')
        
        elif json_data['method'] == 'reply_message':
            username = json_data['username']
            reply = json_data['reply']
            reply_to = json_data['reply_to']
            reply_id = json_data.get('reply_id', None)
            # For creating new reply in thread
            if reply_id == None:
                message_id = json_data['message_id']
                reply_id = str(uuid.uuid4())
                reply_data = {'reply_id': reply_id, 'username': username, 'reply': reply, 'reply_to': reply_to}
                collection_name.update_one({'_id': ObjectId(id), 'messages.message_id': message_id} ,{'$push':{'messages.$.replies': reply_data}}, upsert=True)
                return JsonResponse(reply_data, safe=False, status=200)
                # For editing existing reply in thread
            else:
                reply_data = {'reply_id': reply_id, 'username': username, 'reply': reply, 'reply_to': reply_to}
                our_data = collection_name.find_one({'messages.replies.reply_id': reply_id})
                messages = our_data['messages']
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
                        collection_name.update_one({'_id': ObjectId(id), 'messages.replies.reply_id': reply_id},{'$set':{'messages.$.replies': edited_replies}})
                        return JsonResponse(reply_data, safe=False, status=200)
                return TypeError(f'Could not find reply with reply_id: {reply_id} to delete')
        elif json_data['method'] == 'delete_reply':
            try:
                reply_id = json_data['reply_id']
                our_data = collection_name.find_one({'messages.replies.reply_id': reply_id})
                messages = our_data['messages']
                for message in messages:
                    print(message)
                    reply_was_changed = False
                    replies = message['replies']

                    edited_replies = []
                    for reply_object in replies:
                        if reply_object['reply_id'] != reply_id:
                            edited_replies.append(reply_object)
                        else:
                            reply_was_changed = True
                    if reply_was_changed == True:
                        collection_name.update_one({'_id': ObjectId(id), 'messages.replies.reply_id': reply_id},{'$set':{'messages.$.replies': edited_replies}})
                        return HttpResponse(status=204)
            except:
                return HttpResponseNotFound(f'Could not find reply with reply_id: {reply_id} to delete')
        elif json_data['method'] == 'edit_thread_likes':
            username = json_data['username']
            add_not_take = json_data['add_not_take']
            if add_not_take == True:
                collection_name.update_one({'_id': ObjectId(id)},{'$push': {'likes': username}}, upsert=True)
            elif add_not_take == False:
                collection_name.update_one({'_id': ObjectId(id)},{'$pull': {'likes': username}}, upsert=True)
            else:
                return HttpResponseBadRequest('Check request Body')
            data = collection_name.find_one({'_id': ObjectId(id)})
            likes_array = data['likes']
            return JsonResponse(likes_array, safe=False, status=200)

    elif request.method == 'DELETE':
        collection_name.delete_one({'_id': ObjectId(id)})
        return HttpResponse('Thread deleted', status=202)
    else:
        return HttpResponseBadRequest('Only GET and PATCH requests allowed')


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
    else:
        return HttpResponseBadRequest('Only POST requests allowed')

def not_found_404(request, exception):
    response = {'error': exception}
    return JsonResponse(response, safe=False)


def server_error_500(request):
    response = {'error': '500 Error'}
    return JsonResponse(response, safe=False)

