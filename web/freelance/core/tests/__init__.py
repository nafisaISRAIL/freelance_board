from django.test import TestCase as BaseTestCase
from rest_framework.test import APIClient


class APIViewTestCase(BaseTestCase):
    def setUp(self):
        self.client = APIClient()
