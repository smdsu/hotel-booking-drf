from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookingViewSet

app_name = "booking"

router = DefaultRouter()
router.register(r"booking", BookingViewSet)

urlpatterns = [
    path("", include(router.urls)),
]