from rest_framework.serializers import ModelSerializer, ValidationError
from .models import Booking

class BookingSerializer(ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"

    def validate(self, data):
        room = data.get("room")
        start = data.get("check_in")
        end = data.get("check_out")

        conflicts = Booking.objects.filter(
            room=room,
            check_in__lte=end,
            check_out__gte=start
        )
        if conflicts.exists():
            raise ValidationError("The room is already booked for the selected dates.")
        return data
        