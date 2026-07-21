from rest_framework import serializers

from bookings.models import Resource


class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ["name", "slug", "description", "is_active"]
