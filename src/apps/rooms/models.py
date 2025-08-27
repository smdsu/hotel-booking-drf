from django.db import models
import uuid
from common.mixins import TimeStampMixin


class Room(TimeStampMixin):
    room_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    def __repr__(self) -> str:
        return f"<{self.room_id}> Room {self.description} - {self.price}"

    def __str__(self) -> uuid.UUID:
        return str(self.room_id)
