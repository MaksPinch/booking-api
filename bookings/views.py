from rest_framework import generics

from bookings.models import Resource
from bookings.serializers import ResourceSerializer


class ResourcesListView(generics.ListAPIView):
    queryset = Resource.objects.filter(is_active=True)
    serializer_class = ResourceSerializer


class ResourceDetailView(generics.RetrieveAPIView):
    lookup_field = "slug"
    queryset = Resource.objects.filter(is_active=True)
    serializer_class = ResourceSerializer
