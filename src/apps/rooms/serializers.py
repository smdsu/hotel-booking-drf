from rest_framework.serializers import ModelSerializer
from booking.serializers import BookingSerializer
from .models import Room


class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"

class RoomCreateResponseSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = ["room_id"]

class RoomDetailResponseSerializer(ModelSerializer):
    bookings = BookingSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = ["room_id", "price", "bookings"]
