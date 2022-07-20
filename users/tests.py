from django.test import TestCase
import json
import pymongo
my_client = pymongo.MongoClient('mongodb+srv://readherring:readherring@readherring.qlngl1v.mongodb.net/?retryWrites=true&w=majority')
db = my_client['readherring']
collection_name = db['Users']

class TestUrls(TestCase):

    def testUsersPage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def testUsersByUsernameFail(self):
        response = self.client.get('/users/iadhfbdsjfhbksajdbfsfdfs')
        self.assertEqual(response.status_code, 404)
    
    def testUsersByUsernamePass(self):
        response = self.client.get('/users/user1')
        self.assertEqual(response.status_code, 200) 

    def testUsersUsernamePatchAddToRead(self):
        patch_data = {
            "method": "add_to_read",
  	        "ISBN": "12345",
  	        "title":"title",
  	        "author":"author"
        }
        j_data = json.dumps(patch_data)
        response = self.client.patch('/users/user1', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 204)

    def testUsersUsernamePatchFavourite(self):
        patch_data = {
            "method": "edit_favourite_status",
  	        "ISBN": "12345",
  	        "set_favourited": True
        }
        j_data = json.dumps(patch_data)
        response = self.client.patch('/users/user1', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 204)

    def testUsersUsernamePatchAddWantsToRead(self):
        patch_data = {
            "method": "add_to_wants_to_read",
  	        "ISBN": "12345",
  	        "title":"title",
  	        "author":"author"
        }
        j_data = json.dumps(patch_data)
        response = self.client.patch('/users/user1', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 204)

    def testUsersUsernamePatchAboutMe(self):
        patch_data = {
            "method": "edit_about_me",
            "about_me": "Change about me to this"
        }
        j_data = json.dumps(patch_data)
        response = self.client.patch('/users/user1', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 204)

    def testUsersRegister(self):
        # collection_name.delete_one({'username': "ksadfkjlabdfjak" })
        post_data = {
            "password": "asdyasjdhajsk",
  	        "email": "asdhkbashjd@adjhfbjdsa.com",
  	        "username": "ksadfkjlabdfjak"
        }
        j_data = json.dumps(post_data)
        response = self.client.post('/users/register/', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 201)

    def testUsersRegisterSameDetails(self):
        post_data = {
            "password": "asdyasjdhajsk",
  	        "email": "asdhkbashjd@adjhfbjdsa.com",
  	        "username": "ksadfkjlabdfjak"
        }
        j_data = json.dumps(post_data)
        response = self.client.post('/users/register/', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 409)

    def testUsersLogin(self):
        post_data = {
            "password": "password",
  	        "user_input": "user1"
        }
        j_data = json.dumps(post_data)
        response = self.client.post('/users/login/', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 200)

    def testUsersLoginWrongDetails(self):
        post_data = {
            "password": "asdasd",
  	        "user_input": "user1"
        }
        j_data = json.dumps(post_data)
        response = self.client.post('/users/login/', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 401)
        collection_name.delete_one({'username': 'ksadfkjlabdfjak' })
