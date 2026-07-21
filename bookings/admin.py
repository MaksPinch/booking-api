from django.contrib import admin

from bookings.models import Booking, Resource


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "resource",
        "user",
        "start_time",
        "end_time",
        "status",
        "created_at",
    )
    list_filter = ("resource", "status")
    readonly_fields = ("created_at",)
    search_fields = ("resource__name",)


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "description", "is_active")
    list_filter = ("is_active",)
    search_fields = ("slug", "name")
