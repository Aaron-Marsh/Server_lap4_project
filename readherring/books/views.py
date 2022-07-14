from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("<h1>Hello and welcome to my first <u>Django App</u> project!</h1>")

# from pymongo import MongoClient
# client = pymongo.MongoClient('connection_string')
# db = client['db_name']

import pymongo
# from django.conf import settings
my_client = pymongo.MongoClient('mongodb+srv://readherring:readherring@readherring.qlngl1v.mongodb.net/?retryWrites=true&w=majority')

# First define the database name
dbname = my_client['readherring']

# Now get/create collection name (remember that you will see the database in your mongodb cluster only after you create a collection)
collection_name = dbname['Books']

#let's create two documents
book1 = {
    "title": "first book",
    "author" : "first author"
}
book2 = {
    "title": "second title",
    "author" : "second author",
}

print('hello ******************')

collection_name.insert_many([book1, book2])

books_list = collection_name.find({})

for r in books_list:
	print(r['title'])

# update_data = collection_name.update_one({'medicine_id':'RR000123456'}, {'$set':{'common_name':'Paracetamol 500'}})

# count = collection_name.count()
# print(count)

# delete_data = collection_name.delete_one({'medicine_id':'RR000123456'})

