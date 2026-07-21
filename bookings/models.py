from django.conf import settings
from django.db import models


class Resource(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name", "id"]


class Booking(models.Model):
    ACTIVE_STATUS = "active"
    CANCELLED_STATUS = "cancelled"

    STATUS_CHOICE = [(ACTIVE_STATUS, "Active"), (CANCELLED_STATUS, "Canсelled")]
    resource = models.ForeignKey(
        Resource, on_delete=models.CASCADE, related_name="bookings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="bookings"
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICE, default=ACTIVE_STATUS
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="booking_end_after_start",
            ),
            models.UniqueConstraint(
                fields=["resource", "start_time"],
                condition=models.Q(status="active"),
                name="unique_active_booking_per_slot",
            ),
        ]
        indexes = [
            models.Index(fields=["resource", "start_time"]),
        ]
