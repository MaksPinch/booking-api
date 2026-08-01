from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bookings.models import Booking, Resource
from bookings.permissions import IsOwner
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


class CancelBooking(APIView):
    permission_classes = [IsAuthenticated, IsOwner]

    def post(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)

        self.check_object_permissions(request, booking)

        if booking.status == Booking.CANCELLED_STATUS:
            return Response(
                data={"message": "The reservation has already been canceled"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        booking.status = Booking.CANCELLED_STATUS
        booking.save()

        return Response(
            data={"message": "The reservation has been successfully canceled"},
            status=status.HTTP_200_OK,
        )
