from django.test import TestCase
import json
# Create your tests here.
class TestUrls(TestCase):

    def testHomePage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def testBooksPage(self):
        response = self.client.get('/books/')
        self.assertEqual(response.status_code, 200)

    def testBooksISBNPageGetFail(self):
        response = self.client.get('/books/123')
        self.assertEqual(response.status_code, 404)
    
    def testBooksISBNPageGetPass(self):
        response = self.client.get('/books/12345')
        self.assertEqual(response.status_code, 200)


    # Test insert review
    def testBooksISBNPagePatchReview(self):
        patch_data = {
            "method": "add_review",
            "username": "user",
            "review":"This was good"
            }
        j_data = json.dumps(patch_data)
        response = self.client.patch('/books/12345', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 204)

    # Test add a rating
    def testBooksISBNPagePatchRating(self):
        patch_data = {
            "method": "add_rating",
  	        "username": "user1",
  	        "rating": 4
            }
        j_data = json.dumps(patch_data)
        response = self.client.patch('/books/12345', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 204)
    
    def testBooksApiPage(self):
        response = self.client.get('/books/api/')
        self.assertEqual(response.status_code, 400)

    # Expect to reveive back query result
    def testBooksApiPagePost(self):
        post_data = {
            'query_type': 'intitle',
  	        'query': 'harry potter and the philosopher\'s stone',
  	        'num_results': '3'
            }
        j_data = json.dumps(post_data)
        response = self.client.post('/books/api/', content_type='application/json', data = j_data)
        self.assertEqual(response.status_code, 200)
