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

        # Check if check_out is after check_in
        if start and end and start >= end:
            raise ValidationError("Check-out date must be after check-in date.")

        conflicts = Booking.objects.filter(
            room=room, check_in__lt=end, check_out__gt=start
        )

        if self.instance:
            conflicts = conflicts.exclude(pk=self.instance.pk)

        if conflicts.exists():
            raise ValidationError("The room is already booked for the selected dates.")
        return data
