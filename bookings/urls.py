from django.urls import path

from bookings.views import BookingsListView, ResourceDetailView, ResourcesListView, CancelBooking
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path("api/resources/", ResourcesListView.as_view(), name="all_resources"),
    path(
        "api/resources/<slug:slug>/",
        ResourceDetailView.as_view(),
        name="specific_resource",
    ),
    path("api/bookings/", BookingsListView.as_view(), name="users_bookings"),
    path("api/token/", obtain_auth_token, name="token_authentication"),
    path("api/bookings/<int:booking_id>/cancel/", CancelBooking.as_view(), name="cancel_booking"),
]
