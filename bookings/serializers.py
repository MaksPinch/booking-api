from rest_framework import serializers

from bookings.models import Booking, Resource


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["name", "slug", "description", "is_active"]


class BookingSerializer(serializers.ModelSerializer):
    resource = serializers.SlugRelatedField(
        slug_field="slug", queryset=Resource.objects.all()
    )

    class Meta:
        model = Booking
        fields = ["id", "resource", "start_time", "end_time", "status", "created_at"]
