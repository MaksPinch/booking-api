from django.urls import path

from bookings.views import BookingsListView, ResourceDetailView, ResourcesListView

urlpatterns = [
    path("api/resources/", ResourcesListView.as_view(), name="all_resources"),
    path(
        "api/resources/<slug:slug>/",
        ResourceDetailView.as_view(),
        name="specific_resource",
    ),
    path("api/bookings/", BookingsListView.as_view(), name="users_bookings"),
]
