from decimal import Decimal
from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from rooms.models import Room
from rooms.serializers import (
    RoomSerializer,
    RoomCreateResponseSerializer,
    RoomDetailResponseSerializer,
)
from booking.models import Booking


class RoomModelTest(TestCase):
    def setUp(self):
        self.room_data = {
            "description": "Luxury Suite with Ocean View",
            "price": Decimal("299.99"),
            "active": True,
        }

    def test_room_creation(self):
        room = Room.objects.create(**self.room_data)

        self.assertIsNotNone(room.room_id)
        self.assertEqual(room.description, self.room_data["description"])
        self.assertEqual(room.price, self.room_data["price"])
        self.assertEqual(room.active, self.room_data["active"])
        self.assertIsNotNone(room.created_at)
        self.assertIsNotNone(room.updated_at)

    def test_room_default_values(self):
        room = Room.objects.create(description="Test Room", price=Decimal("100.00"))

        self.assertTrue(room.active)
        self.assertIsNotNone(room.room_id)

    def test_room_string_representation(self):
        room = Room.objects.create(**self.room_data)

        self.assertEqual(str(room), str(room.room_id))

        expected_repr = f"<{room.room_id}> Room {room.description} - {room.price}"
        self.assertEqual(repr(room), expected_repr)

    def test_room_price_decimal_places(self):
        room = Room.objects.create(
            description="Test Room", price=Decimal("99.99"), active=True
        )

        self.assertEqual(room.price, Decimal("99.99"))
        self.assertEqual(str(room.price), "99.99")

    def test_room_description_text_field(self):
        long_description = "This is a very long description " * 10
        room = Room.objects.create(
            description=long_description, price=Decimal("100.00"), active=True
        )

        self.assertEqual(room.description, long_description)
        self.assertGreater(len(room.description), 100)


class RoomSerializerTest(TestCase):
    def setUp(self):
        self.room = Room.objects.create(
            description="Test Room", price=Decimal("150.00"), active=True
        )

    def test_room_serializer_fields(self):
        serializer = RoomSerializer()
        expected_fields = {
            "room_id",
            "description",
            "price",
            "active",
            "created_at",
            "updated_at",
        }
        self.assertEqual(set(serializer.fields.keys()), expected_fields)

    def test_room_serializer_valid_data(self):
        data = {"description": "New Room", "price": "200.00", "active": False}

        serializer = RoomSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_room_serializer_invalid_price(self):
        data = {"description": "Test Room", "price": "invalid_price", "active": True}

        serializer = RoomSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("price", serializer.errors)

    def test_room_create_response_serializer(self):
        serializer = RoomCreateResponseSerializer(self.room)
        data = serializer.data

        self.assertEqual(set(data.keys()), {"room_id"})
        self.assertEqual(data["room_id"], str(self.room.room_id))

    def test_room_detail_response_serializer(self):
        serializer = RoomDetailResponseSerializer(self.room)
        data = serializer.data

        expected_fields = {"room_id", "price", "bookings"}
        self.assertEqual(set(data.keys()), expected_fields)
        self.assertEqual(data["room_id"], str(self.room.room_id))
        self.assertEqual(data["price"], str(self.room.price))
        self.assertEqual(data["bookings"], [])


class RoomViewSetTest(APITestCase):
    def setUp(self):
        self.room = Room.objects.create(
            description="Test Room", price=Decimal("100.00"), active=True
        )

        self.room_data = {"description": "New Room", "price": "150.00", "active": True}

    def test_create_room(self):
        url = reverse("rooms:room-list")
        response = self.client.post(url, self.room_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(set(response.data.keys()), {"room_id"})

        room_id = response.data["room_id"]
        self.assertTrue(Room.objects.filter(room_id=room_id).exists())

        room = Room.objects.get(room_id=room_id)
        self.assertEqual(room.description, self.room_data["description"])
        self.assertEqual(room.price, Decimal(self.room_data["price"]))
        self.assertEqual(room.active, self.room_data["active"])

    def test_list_rooms(self):
        Room.objects.create(description="Room 2", price=Decimal("200.00"), active=False)

        url = reverse("rooms:room-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

        for room in response.data["results"]:
            self.assertIn("room_id", room)
            self.assertIn("description", room)
            self.assertIn("price", room)
            self.assertIn("active", room)
            self.assertIn("created_at", room)
            self.assertIn("updated_at", room)

    def test_retrieve_room(self):
        url = reverse("rooms:room-detail", kwargs={"pk": self.room.room_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["room_id"], str(self.room.room_id))
        self.assertEqual(response.data["price"], str(self.room.price))
        self.assertEqual(response.data["bookings"], [])

    def test_retrieve_room_with_bookings(self):
        check_in = timezone.now() + timedelta(days=1)
        check_out = check_in + timedelta(days=3)

        Booking.objects.create(room=self.room, check_in=check_in, check_out=check_out)

        url = reverse("rooms:room-detail", kwargs={"pk": self.room.room_id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["bookings"]), 1)

        booking_data = response.data["bookings"][0]
        self.assertEqual(str(booking_data["room"]), str(self.room.room_id))
        self.assertIn("check_in", booking_data)
        self.assertIn("check_out", booking_data)

    def test_update_room(self):
        update_data = {
            "description": "Updated Room",
            "price": "250.00",
            "active": False,
        }

        url = reverse("rooms:room-detail", kwargs={"pk": self.room.room_id})
        response = self.client.put(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.room.refresh_from_db()
        self.assertEqual(self.room.description, update_data["description"])
        self.assertEqual(self.room.price, Decimal(update_data["price"]))
        self.assertEqual(self.room.active, update_data["active"])

    def test_partial_update_room(self):
        update_data = {"description": "Partially Updated Room"}

        url = reverse("rooms:room-detail", kwargs={"pk": self.room.room_id})
        response = self.client.patch(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.room.refresh_from_db()
        self.assertEqual(self.room.description, update_data["description"])
        self.assertEqual(self.room.price, Decimal("100.00"))
        self.assertTrue(self.room.active)

    def test_delete_room(self):
        url = reverse("rooms:room-detail", kwargs={"pk": self.room.room_id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Room.objects.count(), 0)

    def test_create_room_invalid_data(self):
        invalid_data = {
            "description": "",
            "price": "invalid_price",
            "active": "not_boolean",
        }

        url = reverse("rooms:room-list")
        response = self.client.post(url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("description", response.data)
        self.assertIn("price", response.data)
        self.assertIn("active", response.data)

    def test_update_room_invalid_data(self):
        invalid_data = {
            "description": "Test Room",
            "price": "-100.00",
            "active": True,
        }

        url = reverse("rooms:room-detail", kwargs={"pk": self.room.room_id})
        response = self.client.put(url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("price", response.data)


class RoomIntegrationTest(APITestCase):
    def setUp(self):
        self.room_data = {
            "description": "Integration Test Room",
            "price": "175.50",
            "active": True,
        }

    def test_complete_room_workflow(self):
        url = reverse("rooms:room-list")
        response = self.client.post(url, self.room_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        room_id = response.data["room_id"]

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        detail_url = reverse("rooms:room-detail", kwargs={"pk": room_id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["room_id"], room_id)

        update_data = {
            "description": "Updated Integration Room",
            "price": "200.00",
            "active": False,
        }

        response = self.client.put(detail_url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["price"], "200.00")

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_room_with_multiple_bookings(self):
        url = reverse("rooms:room-list")
        response = self.client.post(url, self.room_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        room_id = response.data["room_id"]

        room = Room.objects.get(room_id=room_id)

        check_in1 = timezone.now() + timedelta(days=1)
        check_out1 = check_in1 + timedelta(days=2)
        Booking.objects.create(room=room, check_in=check_in1, check_out=check_out1)

        check_in2 = timezone.now() + timedelta(days=5)
        check_out2 = check_in2 + timedelta(days=3)
        Booking.objects.create(room=room, check_in=check_in2, check_out=check_out2)

        detail_url = reverse("rooms:room-detail", kwargs={"pk": room_id})
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["bookings"]), 2)

        bookings = response.data["bookings"]
        self.assertEqual(str(bookings[0]["room"]), str(room_id))
        self.assertEqual(str(bookings[1]["room"]), str(room_id))

    def test_room_filtering_and_search(self):
        Room.objects.create(
            description="Luxury Suite", price=Decimal("500.00"), active=True
        )
        Room.objects.create(
            description="Standard Room", price=Decimal("100.00"), active=True
        )
        Room.objects.create(
            description="Budget Room", price=Decimal("50.00"), active=False
        )

        url = reverse("rooms:room-list")

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)

        if "results" in response.data:
            self.assertIn("count", response.data)
            self.assertIn("next", response.data)
            self.assertIn("previous", response.data)
