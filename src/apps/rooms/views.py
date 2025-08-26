from rest_framework.viewsets import ModelViewSet
from .models import Room
from .serializers import RoomSerializer

class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
