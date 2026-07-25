from rest_framework import generics
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated

from bookings.models import Booking, Resource
from bookings.serializers import BookingSerializer, ResourceSerializer


class ResourcesListView(generics.ListAPIView):
    queryset = Resource.objects.filter(is_active=True)
    serializer_class = ResourceSerializer


class ResourceDetailView(generics.RetrieveAPIView):
    lookup_field = "slug"
    queryset = Resource.objects.filter(is_active=True)
    serializer_class = ResourceSerializer


class BookingsListView(ListCreateAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        queryset = Booking.objects.filter(user=self.request.user)

        resource = self.request.query_params.get("resource")

        if resource is not None:
            queryset = queryset.filter(resource__slug=resource)

        return queryset
