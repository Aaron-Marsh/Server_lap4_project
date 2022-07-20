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

    def testForumPatchMessage(self):
        post_data = {
            "method": "thread_message",
            "username": "User2",
            "message": "this is another message in the thread"
        }
        j_data = json.dumps(post_data)
        response = self.client.patch('/forums/62d739a2f981c7f9185af9b2', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 200)
    
    def testForumPatchMessage(self):
        post_data = {
            "method": "thread_message",
            "username": "User2",
            "message": "this is another message in the thread"
        }
        j_data = json.dumps(post_data)
        response = self.client.patch('/forums/62d739a2f981c7f9185af9b2', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 200)

    def testForumPatchMessageEdit(self):
        post_data = {
            "method": "thread_message",
            "username": "User2",
            "message": "this is another message in the thread",
            "message_id":"11111"
        }
        j_data = json.dumps(post_data)
        response = self.client.patch('/forums/62d739a2f981c7f9185af9b2', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 200)

    def testForumPatchMessageDelete(self):
        post_data = {
            "method": "delete_message",
            "message_id":"11111"
        }
        j_data = json.dumps(post_data)
        response = self.client.patch('/forums/62d739a2f981c7f9185af9b2', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 204)

    def testForumPatchReply(self):
        post_data = {
            "method":"reply_message",
            "username": "user10",
            "reply": "This is a reply to message",
            "message_id": "22222",
            "reply_to": ""
        }
        j_data = json.dumps(post_data)
        response = self.client.patch('/forums/62d739a2f981c7f9185af9b2', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 200)

    def testForumPatchReplyEdit(self):
        post_data = {
            "method":"reply_message",
            "username": "user10",
            "reply": "This is a reply to message",
            "message_id": "22222",
            "reply_to": "",
            "reply_id": "885"
        }
        j_data = json.dumps(post_data)
        response = self.client.patch('/forums/62d739a2f981c7f9185af9b2', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 200)
