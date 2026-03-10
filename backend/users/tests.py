from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User

class UserAPITests(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "phone_number": "5512345678",
            "curp": "TEST900101HDFLRS01"
        }

    def test_create_user(self):
        url = reverse("user-list")
        response = self.client.post(url, self.user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.count() == 1
        assert User.objects.get().email == self.user_data["email"]

    def test_duplicate_email(self):
        User.objects.create_user(**self.user_data)
        url = reverse("user-list")
        response = self.client.post(url, self.user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_curp(self):
        url = reverse("user-list")
        self.user_data["curp"] = "INVALID"
        response = self.client.post(url, self.user_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_self_access(self):
        user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=user)

        # Test list only shows self
        url = reverse("user-list")
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["email"] == user.email

        # Test detail access
        url = reverse("user-detail", args=[user.id])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_isolation(self):
        user1 = User.objects.create_user(**self.user_data)
        user2 = User.objects.create_user(email="other@example.com", curp="OTHR900101HDFLRS02")

        self.client.force_authenticate(user=user1)

        # User1 should NOT see User2 in list
        url = reverse("user-list")
        response = self.client.get(url)
        assert len(response.data) == 1
        assert response.data[0]["id"] == user1.id

        # User1 should NOT be able to access User2 detail
        url = reverse("user-detail", args=[user2.id])
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND
