from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from rooms.models import Room
from booking.models import Booking
from booking.serializers import BookingSerializer


class BookingModelTest(TestCase):
    def setUp(self):
        self.room = Room.objects.create(
            description="Test Room", price=Decimal("100.00"), active=True
        )

    def test_booking_creation(self):
        check_in = timezone.now() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        booking = Booking.objects.create(
            room=self.room, check_in=check_in, check_out=check_out
        )

        self.assertIsNotNone(booking.id)
        self.assertEqual(booking.room, self.room)
        self.assertEqual(booking.check_in, check_in)
        self.assertEqual(booking.check_out, check_out)
        self.assertIsNotNone(booking.created_at)
        self.assertIsNotNone(booking.updated_at)

    def test_booking_string_representation(self):
        check_in = timezone.now() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        booking = Booking.objects.create(
            room=self.room, check_in=check_in, check_out=check_out
        )

        expected_str = f"Booking on {self.room} - Dates: {check_in} - {check_out}"
        self.assertEqual(str(booking), expected_str)

    def test_booking_repr_representation(self):
        check_in = timezone.now() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        booking = Booking.objects.create(
            room=self.room, check_in=check_in, check_out=check_out
        )

        expected_repr = f"Booking: {booking.id}"
        self.assertEqual(repr(booking), expected_repr)


class BookingSerializerTest(TestCase):
    def setUp(self):
        self.room = Room.objects.create(
            description="Test Room", price=Decimal("100.00"), active=True
        )

    def test_valid_booking_data(self):
        check_in = timezone.now() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        data = {"room": self.room.room_id, "check_in": check_in, "check_out": check_out}

        serializer = BookingSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_invalid_dates_check_out_before_check_in(self):
        check_in = timezone.now() + timedelta(days=2)
        check_out = timezone.now() + timedelta(days=1)

        data = {"room": self.room.room_id, "check_in": check_in, "check_out": check_out}

        serializer = BookingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertIn(
            "Check-out date must be after check-in date",
            str(serializer.errors["non_field_errors"][0]),
        )

    def test_booking_conflict_detection(self):
        existing_check_in = timezone.now() + timedelta(days=1)
        existing_check_out = existing_check_in + timedelta(days=3)

        Booking.objects.create(
            room=self.room, check_in=existing_check_in, check_out=existing_check_out
        )

        conflicting_check_in = existing_check_in + timedelta(days=1)
        conflicting_check_out = conflicting_check_in + timedelta(days=2)

        data = {
            "room": self.room.room_id,
            "check_in": conflicting_check_in,
            "check_out": conflicting_check_out,
        }

        serializer = BookingSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("non_field_errors", serializer.errors)
        self.assertIn("already booked", str(serializer.errors["non_field_errors"][0]))

    def test_booking_conflict_edge_cases(self):
        existing_check_in = timezone.now() + timedelta(days=1)
        existing_check_out = existing_check_in + timedelta(days=3)

        Booking.objects.create(
            room=self.room, check_in=existing_check_in, check_out=existing_check_out
        )

        non_conflicting_check_in = existing_check_out
        non_conflicting_check_out = non_conflicting_check_in + timedelta(days=1)

        data = {
            "room": self.room.room_id,
            "check_in": non_conflicting_check_in,
            "check_out": non_conflicting_check_out,
        }

        serializer = BookingSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        non_conflicting_check_in2 = existing_check_in - timedelta(days=1)
        non_conflicting_check_out2 = existing_check_in

        data2 = {
            "room": self.room.room_id,
            "check_in": non_conflicting_check_in2,
            "check_out": non_conflicting_check_out2,
        }

        serializer2 = BookingSerializer(data=data2)
        self.assertTrue(serializer2.is_valid())

        overlapping_check_in = existing_check_in + timedelta(hours=12)
        overlapping_check_out = existing_check_out - timedelta(hours=12)

        data3 = {
            "room": self.room.room_id,
            "check_in": overlapping_check_in,
            "check_out": overlapping_check_out,
        }

        serializer3 = BookingSerializer(data=data3)
        self.assertFalse(serializer3.is_valid())
        self.assertIn("already booked", str(serializer3.errors["non_field_errors"][0]))

    def test_serializer_fields(self):
        serializer = BookingSerializer()
        expected_fields = {
            "id",
            "room",
            "check_in",
            "check_out",
            "created_at",
            "updated_at",
        }
        self.assertEqual(set(serializer.fields.keys()), expected_fields)


class BookingViewSetTest(APITestCase):
    def setUp(self):
        self.room = Room.objects.create(
            description="Test Room", price=Decimal("100.00"), active=True
        )

        self.check_in = timezone.now() + timedelta(days=1)
        self.check_out = self.check_in + timedelta(days=2)

        self.booking_data = {
            "room": self.room.room_id,
            "check_in": self.check_in,
            "check_out": self.check_out,
        }

    def test_create_booking(self):
        url = reverse("booking:booking-list")
        response = self.client.post(url, self.booking_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)

        booking = Booking.objects.first()
        self.assertEqual(booking.room, self.room)
        self.assertEqual(booking.check_in, self.check_in)
        self.assertEqual(booking.check_out, self.check_out)

    def test_list_bookings(self):
        Booking.objects.create(
            room=self.room, check_in=self.check_in, check_out=self.check_out
        )

        Booking.objects.create(
            room=self.room,
            check_in=self.check_in + timedelta(days=5),
            check_out=self.check_out + timedelta(days=5),
        )

        url = reverse("booking:booking-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)

    def test_retrieve_booking(self):
        booking = Booking.objects.create(
            room=self.room, check_in=self.check_in, check_out=self.check_out
        )

        url = reverse("booking:booking-detail", kwargs={"pk": booking.id})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(booking.id))
        self.assertEqual(str(response.data["room"]), str(booking.room.room_id))

    def test_update_booking(self):
        booking = Booking.objects.create(
            room=self.room, check_in=self.check_in, check_out=self.check_out
        )

        new_check_out = self.check_out + timedelta(days=1)
        update_data = {
            "room": self.room.room_id,
            "check_in": self.check_in,
            "check_out": new_check_out,
        }

        url = reverse("booking:booking-detail", kwargs={"pk": booking.id})
        response = self.client.put(url, update_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        booking.refresh_from_db()
        self.assertEqual(booking.check_out, new_check_out)

    def test_delete_booking(self):
        booking = Booking.objects.create(
            room=self.room, check_in=self.check_in, check_out=self.check_out
        )

        url = reverse("booking:booking-detail", kwargs={"pk": booking.id})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Booking.objects.count(), 0)

    def test_create_booking_with_conflict(self):
        Booking.objects.create(
            room=self.room, check_in=self.check_in, check_out=self.check_out
        )

        conflicting_data = {
            "room": self.room.room_id,
            "check_in": self.check_in + timedelta(hours=12),
            "check_out": self.check_out + timedelta(hours=12),
        }

        url = reverse("booking:booking-list")
        response = self.client.post(url, conflicting_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already booked", str(response.data))

    def test_invalid_booking_data(self):
        invalid_data = {
            "room": self.room.room_id,
            "check_in": "invalid_date",
            "check_out": "invalid_date",
        }

        url = reverse("booking:booking-list")
        response = self.client.post(url, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("check_in", response.data)
        self.assertIn("check_out", response.data)


class BookingIntegrationTest(APITestCase):
    def setUp(self):
        self.room = Room.objects.create(
            description="Luxury Suite", price=Decimal("250.00"), active=True
        )

        self.room2 = Room.objects.create(
            description="Standard Room", price=Decimal("100.00"), active=True
        )

    def test_complete_booking_workflow(self):
        check_in = timezone.now() + timedelta(days=1)
        check_out = check_in + timedelta(days=3)

        booking_data = {
            "room": self.room.room_id,
            "check_in": check_in,
            "check_out": check_out,
        }

        url = reverse("booking:booking-list")
        response = self.client.post(url, booking_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        booking_id = response.data["id"]

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)

        new_check_out = check_out + timedelta(days=1)
        update_data = {
            "room": self.room.room_id,
            "check_in": check_in,
            "check_out": new_check_out,
        }

        detail_url = reverse("booking:booking-detail", kwargs={"pk": booking_id})
        response = self.client.put(detail_url, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_check_out = response.data["check_out"]
        expected_check_out = new_check_out.isoformat()

        response_check_out_clean = response_check_out.replace("Z", "+00:00")
        self.assertEqual(response_check_out_clean, expected_check_out)

        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 0)

    def test_multiple_rooms_booking_scenario(self):
        check_in = timezone.now() + timedelta(days=1)
        check_out = check_in + timedelta(days=2)

        booking1_data = {
            "room": self.room.room_id,
            "check_in": check_in,
            "check_out": check_out,
        }

        url = reverse("booking:booking-list")
        response = self.client.post(url, booking1_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        booking2_data = {
            "room": self.room2.room_id,
            "check_in": check_in,
            "check_out": check_out,
        }

        response = self.client.post(url, booking2_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        conflicting_data = {
            "room": self.room.room_id,
            "check_in": check_in + timedelta(hours=12),
            "check_out": check_out + timedelta(hours=12),
        }

        response = self.client.post(url, conflicting_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.get(url)
        self.assertEqual(len(response.data["results"]), 2)
