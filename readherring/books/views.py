from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from bson.json_util import loads, dumps
import json

import pymongo
my_client = pymongo.MongoClient('mongodb+srv://readherring:readherring@readherring.qlngl1v.mongodb.net/?retryWrites=true&w=majority')

db = my_client['readherring']

collection_name = db['Books']

collection_name.drop({})
#let's create two documents
book1 = {
    "title": "first book",
    "author": "first author",
    "ISBN": "12345",
    "reviews": []
}
book2 = {
    "title": "second title",
    "author" : "second author",
    "ISBN": "54321",
    "reviews": []
}

collection_name.insert_many([book1, book2])

books_list = collection_name.find({})

# for r in books_list:
# 	print(r)
# print(dumps(books_list))

# Create your views here.
def index(request):
    return HttpResponse("<h1>Hello and welcome to my first <u>Django App</u> project!</h1>")

def get_create_books(request):
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
                






# update_data = collection_name.update_one({'medicine_id':'RR000123456'}, {'$set':{'common_name':'Paracetamol 500'}})

# count = collection_name.count()
# print(count)

# delete_data = collection_name.delete_one({'medicine_id':'RR000123456'})

