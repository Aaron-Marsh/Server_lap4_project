from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from bson.json_util import loads, dumps


import pymongo
my_client = pymongo.MongoClient('mongodb+srv://readherring:readherring@readherring.qlngl1v.mongodb.net/?retryWrites=true&w=majority')

dbname = my_client['readherring']

collection_name = dbname['Books']

collection_name.drop({})
#let's create two documents
book1 = {
    "title": "first book",
    "author" : "first author"
}
book2 = {
    "title": "second title",
    "author" : "second author",
}

collection_name.insert_many([book1, book2])

books_list = collection_name.find({})

# for r in books_list:
# 	print(r)
# print(dumps(books_list))

# Create your views here.
def index(request):
    return HttpResponse("<h1>Hello and welcome to my first <u>Django App</u> project!</h1>")

def getall(request):
    book_list = []
    data = collection_name.find({})
    for book in data:
        book['id'] = str(book['_id'])
        book.pop('_id', None)
        book_list.append(book)
    return JsonResponse(book_list, safe=False)


# update_data = collection_name.update_one({'medicine_id':'RR000123456'}, {'$set':{'common_name':'Paracetamol 500'}})

# count = collection_name.count()
# print(count)

# delete_data = collection_name.delete_one({'medicine_id':'RR000123456'})

