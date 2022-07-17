# from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from bson.json_util import loads, dumps
import json
import requests

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
    "reviews": [],
    "rating": 0,
    "num_ratings": 0
}
book2 = {
    "title": "second title",
    "author" : "second author",
    "ISBN": "54321",
    "reviews": [],
    "rating": 0,
    "num_ratings": 0
}

collection_name.insert_many([book1, book2])

# books_list = collection_name.find({})

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
        data = request.body.decode('utf-8')
        json_data = json.loads(data)
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
        body = request.body.decode('utf-8')
        json_data = json.loads(body)
        if json_data['method'] == 'add_review':
            username = json_data['username']
            review = json_data['review']
            collection_name.update_one({'ISBN': ISBN_string},{'$push':{'reviews': {'username': username, 'review': review}}}, upsert=True)
            return HttpResponse('Review Added to Database')
        

def get_books_from_api(request):
    body = request.body.decode('utf-8')
    j_body = json.loads(body)
    response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={j_body.get('query_type', '')}:{j_body['query']}&max_results={j_body.get('num_results', '5')}")
    json_res = response.json()
    books = []
    for book in json_res["items"]:
        ISBN = book['volumeInfo']['industryIdentifiers'][0]['identifier']
        collection_name.update_one({'ISBN': ISBN},{'$set':{'ISBN': ISBN}}, upsert=True)
        our_data = collection_name.find({'ISBN': ISBN})
        our_book = our_data[0]
        combined_book = {
            'title': book.get('volumeInfo',{}).get('title', 'Title Not Found'),
            'author': book.get('volumeInfo',{}).get('authors', 'Author Not Found'),
            'ISBN': ISBN,
            'publisher': book.get('volumeInfo',{}).get('publisher', 'Publisher Not Found'),
            'publishedDate': book.get('volumeInfo',{}).get('publishedDate', 'Published Date Not Found'),
            'description': book.get('volumeInfo',{}).get('description', 'Description Not Found'),
            'images': book.get('volumeInfo',{}).get('imageLinks', 'No Image Found'),
            'reviews': our_book.get('reviews', []),
            'rating': our_book.get('rating', 0),
            'num_ratings': our_book.get('num_rating', 0)
        }
        books.append(combined_book)
    
    return JsonResponse(books, safe=False)



# update_data = collection_name.update_one({'medicine_id':'RR000123456'}, {'$set':{'common_name':'Paracetamol 500'}})

# count = collection_name.count()
# print(count)

# delete_data = collection_name.delete_one({'medicine_id':'RR000123456'})

