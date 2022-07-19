from django.test import TestCase

# Create your tests here.
class TestUrls(TestCase):

    def testHomePage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def testBooksPage(self):
        response = self.client.get('/books/')
        self.assertEqual(response.status_code, 200)

    def testBooksISBNPage(self):
        response = self.client.get('/books/123')
        self.assertEqual(response.status_code, 200)

    def testBooksApiPage(self):
        response = self.client.get('/books/api/')
        self.assertEqual(response.status_code, 200)
