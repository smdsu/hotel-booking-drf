import uuid

from django.db import models
from common.mixins import TimeStampMixin

class Booking(TimeStampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room = models.ForeignKey("rooms.Room", on_delete=models.CASCADE, related_name="bookings")
    check_in = models.DateTimeField()
    check_out = models.DateTimeField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
