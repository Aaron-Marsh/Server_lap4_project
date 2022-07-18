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


# Create your views here.
def index(request):
    return HttpResponse("<h1>This is the backend of Read Herring!</h1>")

def get_create_books(request):
    if request.method == 'GET':
        try:
            book_list = []
            data = collection_name.find({})
            for book in data:
                book['id'] = str(book['_id'])
                book.pop('_id', None)
                book_list.append(book)
            return JsonResponse(book_list, safe=False)
        except TypeError:
            return HttpResponse('Could not find any books in the database')
    elif request.method == 'POST':
        try:
            data = request.body.decode('utf-8')
            json_data = json.loads(data)
            title = json_data['title']
            author = json_data['author']
            ISBN = json_data['ISBN']
            collection_name.insert_one({"title": title,"author": author,"ISBN": ISBN, "reviews": []})
            book = collection_name.find_one({'ISBN': ISBN})
            book['id'] = str(book['_id'])
            book.pop('_id', None)
            return JsonResponse(book, safe=False)
        except KeyError:
            return HttpResponse('Invalid post, check request.body')
    else:
        return HttpResponse('Only GET and POST requests allowed')

def get_by_ISBN(request, ISBN):
    ISBN_string = str(ISBN)
    if request.method == 'GET':
        try:
            book = collection_name.find_one({'ISBN': ISBN_string})
            book['id'] = str(book['_id'])
            book.pop('_id', None)
            return JsonResponse(book, safe=False)
        except TypeError:
            return HttpResponse(f'Could not find book with ISBN: {ISBN_string} in database')
       
    elif request.method == 'PATCH':
        body = request.body.decode('utf-8')
        json_data = json.loads(body)
        if json_data['method'] == 'add_review':
            username = json_data['username']
            review = json_data['review']
            collection_name.update_one({'ISBN': ISBN_string},{'$push':{'reviews': {'username': username, 'review': review}}}, upsert=True)
            return HttpResponse('Review Added to Database')
        elif json_data['method'] == 'add_rating':
            collection_name.update_one({'ISBN': ISBN_string},{'$inc':{'rating': 0, 'num_ratings': 0}}, upsert=True)
            book = collection_name.find_one({'ISBN': ISBN_string})
            original_average_rating = book['rating']
            original_num_ratings = book['num_ratings']
            personal_rating = json_data['rating']
            new_num_ratings = int(original_num_ratings + personal_rating / abs(personal_rating))
            if new_num_ratings != 0:
                new_average_rating = (original_average_rating * original_num_ratings + personal_rating) / new_num_ratings
            else:
                new_average_rating = 0
            username = json_data['username']
            collection_name.update_one({'ISBN': ISBN_string},{'$set':{'rating': new_average_rating, 'num_ratings': new_num_ratings}})
            db['Users'].update_one({'username': username, "has_read.ISBN": ISBN_string} ,{'$inc':{'has_read.$.personal_rating': personal_rating}})
            return HttpResponse(f'Rating Updated in Database for {username}')
    else:
        return HttpResponse('Only GET and PATCH requests allowed')

def get_books_from_api(request):
    if request.method == 'POST':
        body = request.body.decode('utf-8')
        j_body = json.loads(body)
        query_type = j_body.get('query_type', 'intitle')
        query = j_body.get('query', 'Harry Potter')
        num_results = j_body.get('num_results', '5')
        response = requests.get(f"https://www.googleapis.com/books/v1/volumes?q={query_type}:{query}&max_results={num_results}")
        json_res = response.json()
        books = []
        for book in json_res["items"]:
            ISBN = book['volumeInfo']['industryIdentifiers'][0]['identifier']
            collection_name.update_one({'ISBN': ISBN},{'$set':{'ISBN': ISBN}}, upsert=True)
            our_book = collection_name.find_one({'ISBN': ISBN})
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
                'num_ratings': our_book.get('num_ratings', 0)
            }
            books.append(combined_book)
        return JsonResponse(books, safe=False)
    else:
        return HttpResponse('Only POST requests allowed')

def not_found_404(request, exception):
    response = {'error': exception}
    return JsonResponse(response, safe=False)


def server_error_500(request):
    response = {'error': '500 Error'}
    return HttpResponse('500 error')

