from rest_framework.serializers import ModelSerializer
from .models import Room

class RoomSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = "__all__"

class RoomCreateResponseSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = ["room_id"]
