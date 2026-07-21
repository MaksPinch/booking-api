from django.urls import path

from bookings.views import ResourceDetailView, ResourcesListView

urlpatterns = [
    path("api/resources/", ResourcesListView.as_view()),
    path("api/resources/<slug:slug>/", ResourceDetailView.as_view()),
]
