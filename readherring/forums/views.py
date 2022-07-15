from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from bson.json_util import loads, dumps
import json

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
        book_list = []
        data = collection_name.find({})
        for book in data:
            book['id'] = str(book['_id'])
            book.pop('_id', None)
            book_list.append(book)
        return JsonResponse(book_list, safe=False)
    elif request.method == 'POST':
        # data = request.body
        data = request.body.decode('utf-8')
        json_data = json.loads(data)
        # print(type(data))
        title = json_data['title']
        author = json_data['author']
        ISBN = json_data['ISBN']
        collection_name.insert_one({"title": title,"author": author,"ISBN": ISBN, "reviews": []})
        data = collection_name.find({'ISBN': ISBN})
        book = data[0]
        book['id'] = str(book['_id'])
        book.pop('_id', None)
        return JsonResponse(book, safe=False)
    else:
        print('error')

def get_by_ISBN(request, ISBN):
    ISBN_string = str(ISBN)
    if request.method == 'GET':
        data = collection_name.find({'ISBN': ISBN_string})
        book = data[0]
        book['id'] = str(book['_id'])
        book.pop('_id', None)
        return JsonResponse(book, safe=False)
    elif request.method == 'PATCH':
        data = request.body.decode('utf-8')
        json_data = json.loads(data)
        if json_data['method'] == 'add_review':
            username = json_data['username']
            review = json_data['review']
            collection_name.update_one({'ISBN': ISBN_string},{'$push':{'reviews': {'username': username, 'review': review}}}, upsert=True)
            return HttpResponse('Review Added to Database')
        
        elif json_data['method'] == 'forums':
            if json_data['sub_method'] == 'new_thread':
                username = json_data['username']
                title = json_data['thread_title']
                first_message = json_data['first_message']
                collection_name.update_one({'ISBN': ISBN_string},{'$push':{'threads': {'username': username, 'title': title, 'first_message': first_message }}}, upsert=True)
                return HttpResponse('New Thread Added to Database')
            # elif json_data['sub_method'] == 'thread_message':
                


