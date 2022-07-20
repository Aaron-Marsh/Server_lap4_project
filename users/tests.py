from django.test import TestCase
import json

class TestUrls(TestCase):

    def testHomePage(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


