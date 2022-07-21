# from django.shortcuts import render
from gc import collect
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
from bson.json_util import loads, dumps
import json
import requests

import pymongo
my_client = pymongo.MongoClient('mongodb+srv://readherring:readherring@readherring.qlngl1v.mongodb.net/?retryWrites=true&w=majority')

db = my_client['readherring']
collection_name = db['Books']

from books.seeds import book_seeds
# collection_name.drop({})
# collection_name.insert_many(book_seeds)


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
            return JsonResponse(book_list, safe=False, status=200)
        except TypeError:
            return HttpResponseNotFound('Could not find any books in the database')

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
            return HttpResponseBadRequest('Invalid post, check request.body')
    else:
        return HttpResponseBadRequest('Only GET and POST requests allowed')

def get_by_ISBN(request, ISBN):
    ISBN_string = str(ISBN)
    if request.method == 'GET':
        try:
            book = collection_name.find_one({'ISBN': ISBN_string})
            book['id'] = str(book['_id'])
            book.pop('_id', None)
            return JsonResponse(book, safe=False, status=200)
        except TypeError:
            return HttpResponseNotFound(f'Could not find book with ISBN: {ISBN_string} in database')
       
    elif request.method == 'PATCH':
        body = request.body.decode('utf-8')
        json_data = json.loads(body)
        if json_data['method'] == 'add_review':
            username = json_data['username']
            review = json_data['review']
            collection_name.update_one({'ISBN': ISBN_string},{'$push':{'reviews': {'username': username, 'review': review}}}, upsert=True)
            return HttpResponse(status=204)
        elif json_data['method'] == 'add_rating':
            # collection_name.update_one({'ISBN': ISBN_string},{'$inc':{'rating': 0, 'num_ratings': 0}}, upsert=True)
            # book = collection_name.find_one({'ISBN': ISBN_string})
            # original_average_rating = book['rating']
            # original_num_ratings = book['num_ratings']
            # personal_rating = json_data['rating']
            # new_num_ratings = int(original_num_ratings + personal_rating / abs(personal_rating))
            # if new_num_ratings != 0:
            #     new_average_rating = (original_average_rating * original_num_ratings + personal_rating) / new_num_ratings
            # else:
            #     new_average_rating = 0
            # username = json_data['username']
            # collection_name.update_one({'ISBN': ISBN_string},{'$set':{'rating': new_average_rating, 'num_ratings': new_num_ratings}})
            # db['Users'].update_one({'username': username, "has_read.ISBN": ISBN_string} ,{'$inc':{'has_read.$.personal_rating': personal_rating}})
            username = json_data['username']
            old_rating = json_data['old_rating']
            new_rating = json_data['new_rating']
            book = collection_name.find_one({'ISBN': ISBN_string})
            original_average_rating = book['rating']
            original_num_ratings = book['num_ratings']
            collection_name.update_one({'ISBN': ISBN_string},{'$inc':{'rating': 0, 'num_ratings': 0}}, upsert=True)
            if old_rating == 0:
                new_num_ratings = original_num_ratings + 1
                new_average_rating = (original_average_rating * original_num_ratings + new_rating) / new_num_ratings
            elif new_rating == 0:
                new_num_ratings = original_num_ratings - 1
                new_average_rating = (original_average_rating * original_num_ratings - old_rating) / new_num_ratings
            else:
                new_num_ratings = original_num_ratings
                new_average_rating = (original_average_rating * original_num_ratings + new_rating - old_rating) / new_num_ratings
            collection_name.update_one({'ISBN': ISBN_string},{'$set':{'rating': new_average_rating, 'num_ratings': new_num_ratings}})
            db['Users'].update_one({'username': username, "has_read.ISBN": ISBN_string} ,{'$set':{'has_read.$.personal_rating': new_rating}})
            # collection_name.update_one({'ISBN': ISBN_string}, {'$pull': {'ratings':{'username':username}}}, upsert=True)
            # collection_name.update_one({'ISBN': ISBN_string}, {'$push': {'ratings': rating_object}}, upsert=True)
            response = {'personal_rating': new_rating, 'rating': new_average_rating, 'num_ratings': new_num_ratings}
            return JsonResponse(response, status=200)
        elif json_data['method'] == 'remove_rating':
            username = json_data['username']
            collection_name.update_one({'ISBN': ISBN_string}, {'$pull': {'ratings':{'username':username}}}, upsert=True)
            return HttpResponse(status=204)
    else:
        return HttpResponseBadRequest('Only GET and PATCH requests allowed')

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
            book_data = book.get('volumeInfo', {})
            ISBN = book_data['industryIdentifiers'][0]['identifier']
            collection_name.update_one({'ISBN': ISBN},{'$set':{'ISBN': ISBN}}, upsert=True)
            our_book = collection_name.find_one({'ISBN': ISBN})
            combined_book = {
                'title': book_data.get('title', 'Title Not Found'),
                'author': book_data.get('authors', 'Author Not Found'),
                'ISBN': ISBN,
                'publisher': book_data.get('publisher', 'Publisher Not Found'),
                'publishedDate': book_data.get('publishedDate', 'Published Date Not Found'),
                'description': book_data.get('description', 'Description Not Found'),
                'images': book_data.get('imageLinks', 'No Image Found'),
                'reviews': our_book.get('reviews', []),
                'rating': our_book.get('rating', 0),
                'num_ratings': our_book.get('num_ratings', 0)
            }
            books.append(combined_book)
        sorted_books = sorted(books, key = lambda x: x['num_ratings'], reverse=True)

        return JsonResponse(sorted_books, safe=False, status=200)
    else:
        return HttpResponseBadRequest('Only POST requests allowed')

def not_found_404(request, exception):
    response = {'error': exception}
    return JsonResponse(response, safe=False)


def server_error_500(request):
    response = {'error': '500 Error'}
    return HttpResponse('500 error')

