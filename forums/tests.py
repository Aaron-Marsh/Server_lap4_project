from django.test import TestCase
import json

class TestUrls(TestCase):

    def testForumsPage(self):
        response =  self.client.get('/forums/')
        self.assertEqual(response.status_code, 200)

    def testForumsPagePost(self):
        post_data = {
            "title": "new thread here",
  	        "username": "user",
  	        "first_message": "this is the first message"
        }
        j_data = json.dumps(post_data)
        response = self.client.post('/forums/', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 200)
    
    def testForumByIdPageGetPass(self):
        response = self.client.get('/forums/62d739a2f981c7f9185af9b2')
        self.assertEqual(response.status_code, 200)

    