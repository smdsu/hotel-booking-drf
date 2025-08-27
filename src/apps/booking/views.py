from rest_framework.viewsets import ModelViewSet
from .models import Booking
from .serializers import BookingSerializer


class BookingViewSet(ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
