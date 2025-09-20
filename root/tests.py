# Create your tests here.
from django.test import TestCase


class RootTests(TestCase):
    def test_root(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'root/index.html')