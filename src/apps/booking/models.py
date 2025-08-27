import uuid

from django.db import models
from common.mixins import TimeStampMixin


class Booking(TimeStampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey(
        "rooms.Room", on_delete=models.CASCADE, related_name="bookings"
    )
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()

    def __repr__(self):
        return f"Booking: {self.id}"

    def __str__(self):
        return f"Booking on {self.room} - Dates: {self.check_in} - {self.check_out}"
