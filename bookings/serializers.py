from django.utils import timezone
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

    def validate(self, data):
        resource = data["resource"]
        start = data["start_time"]
        end = data["end_time"]

        if end <= start:
            raise serializers.ValidationError(
                "The end time cannot be earlier than or equal to the start time."
            )
        if start < timezone.now():
            raise serializers.ValidationError("Start time cannot be in the past.")

        overlap = Booking.objects.filter(
            resource=resource,
            status=Booking.ACTIVE_STATUS,
            start_time__lt=end,
            end_time__gt=start,
        )

        if overlap.exists():
            raise serializers.ValidationError("That time slot is already taken")
        return data

    class Meta:
        model = Booking
        fields = ["id", "resource", "start_time", "end_time", "status", "created_at"]
