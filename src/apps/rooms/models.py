from django.db import models
import uuid
from common.mixins import TimeStampMixin


class Room(TimeStampMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    active = models.BooleanField(default=True)

    def __repr__(self):
        return f"<{self.id}> Room {self.name} - {self.price}"

    def __str__(self):
        return self.name
