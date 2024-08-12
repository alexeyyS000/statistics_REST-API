from rest_framework import status
from rest_framework.test import APITestCase

from .models import Poll


class YourModelTests(APITestCase):
    def setUp(self):
        Poll.objects.create(my_field="A", another_field=1)
        Poll.objects.create(my_field="B", another_field=2)
        Poll.objects.create(my_field="C", another_field=3)

    def test_list_yourmodel(self):
        response = self.client.get("/api/yourmodel/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)

    def test_ordering_by_my_field(self):
        response = self.client.get("/api/yourmodel/?ordering=my_field")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Проверяем порядок объектов
        self.assertEqual(response.data[0]["my_field"], "A")
        self.assertEqual(response.data[1]["my_field"], "B")
        self.assertEqual(response.data[2]["my_field"], "C")

    def test_ordering_by_another_field_desc(self):
        response = self.client.get("/api/yourmodel/?ordering=-another_field")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["another_field"], 3)
        self.assertEqual(response.data[1]["another_field"], 2)
        self.assertEqual(response.data[2]["another_field"], 1)

    def test_filtering_by_my_field(self):
        response = self.client.get("/api/yourmodel/?my_field=B")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["my_field"], "B")
