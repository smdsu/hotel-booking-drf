from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone

from rooms.models import Room
from booking.models import Booking


class RoomAPITests(APITestCase):
    def setUp(self):
        self.list_url = "/api/v1/rooms/"

    def test_create_room_returns_only_room_id(self):
        payload = {"description": "Deluxe suite", "price": "199.99", "active": True}
        response = self.client.post(self.list_url, data=payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()), {"room_id"})
        self.assertTrue(Room.objects.filter(room_id=response.data["room_id"]).exists())

    def test_list_rooms(self):
        Room.objects.create(description="A", price="10.00", active=True)
        Room.objects.create(description="B", price="20.00", active=False)

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

        for item in response.data["results"]:
            self.assertIn("room_id", item)
            self.assertIn("description", item)
            self.assertIn("price", item)
            self.assertIn("active", item)

    def test_retrieve_room_includes_nested_bookings(self):
        room = Room.objects.create(description="Sea view", price="150.00", active=True)
        start = timezone.now()
        end = start + timezone.timedelta(days=2)
        Booking.objects.create(room=room, check_in=start, check_out=end)

        detail_url = f"{self.list_url}{room.room_id}/"
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(set(response.data.keys()), {"room_id", "price", "bookings"})
        self.assertEqual(str(response.data["room_id"]), str(room.room_id))
        self.assertEqual(str(response.data["price"]), "150.00")
        self.assertIsInstance(response.data["bookings"], list)
        self.assertEqual(len(response.data["bookings"]), 1)
        booking_payload = response.data["bookings"][0]
        self.assertEqual(str(booking_payload["room"]), str(room.room_id))
        self.assertIn("check_in", booking_payload)
        self.assertIn("check_out", booking_payload)

    def test_update_room_uses_default_serializer(self):
        room = Room.objects.create(description="Old", price="50.00", active=True)
        detail_url = f"{self.list_url}{room.room_id}/"

        response = self.client.patch(
            detail_url, {"description": "New", "active": False}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertIn("description", response.data)
        self.assertEqual(response.data["description"], "New")
        self.assertIn("active", response.data)
        self.assertFalse(response.data["active"])


class RoomModelTests(APITestCase):
    def test_repr_and_str(self):
        room = Room.objects.create(description="Cozy", price="80.00", active=True)

        repr_text = repr(room)
        self.assertIn("Room", repr_text)
        self.assertIn("Cozy", repr_text)
        self.assertIn("80.00", repr_text)

        self.assertEqual(str(room), str(room.room_id))
