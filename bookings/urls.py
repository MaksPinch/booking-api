from django.urls import path

from bookings.views import BookingsListView, ResourceDetailView, ResourcesListView

urlpatterns = [
    path("api/resources/", ResourcesListView.as_view()),
    path("api/resources/<slug:slug>/", ResourceDetailView.as_view()),
    path("api/bookings/", BookingsListView.as_view()),
]
