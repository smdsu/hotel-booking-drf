from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema
from .models import Room
from .serializers import RoomSerializer, RoomCreateResponseSerializer, RoomDetailResponseSerializer


class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return RoomDetailResponseSerializer
        return RoomSerializer

    @extend_schema(
            request=RoomSerializer,
            responses=RoomCreateResponseSerializer
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        response_serializer = RoomCreateResponseSerializer(serializer.instance)
        return Response(response_serializer.data, status=201)
