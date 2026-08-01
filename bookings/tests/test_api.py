from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from bookings.models import Booking, Resource


@pytest.mark.django_db
def test_resource_pagination():
    Resource.objects.create(
        name="Conference Room 1",
        slug="conferenceroom-1",
        description="A small room for 6 people",
        is_active=True,
    )
    Resource.objects.create(
        name="Conference Room 2",
        slug="conferenceroom-2",
        description="A large room for 10 people",
        is_active=True,
    )
    Resource.objects.create(
        name="Conference Room 3",
        slug="conferenceroom-3",
        description="A large room for 20 people with a projector",
        is_active=True,
    )
    client = APIClient()
    url = reverse("all_resources")

    response = client.get(url)

    assert response.status_code == 200
    assert "next" in response.data
    assert "previous" in response.data
    assert "count" in response.data
    assert "results" in response.data


@pytest.mark.django_db
def test_user_bookings():
    User = get_user_model()

    user_a = User.objects.create_user(username="user_a", password="12345")

    user_b = User.objects.create_user(username="user_b", password="1313")

    resource = Resource.objects.create(
        name="Conference Room 1",
        slug="conferenceroom-1",
        description="A small room for 6 people",
        is_active=True,
    )

    booking = Booking.objects.create(
        resource=resource,
        user=user_a,
        start_time=timezone.now(),
        end_time=(timezone.now() + timedelta(hours=2)),
        status=Booking.ACTIVE_STATUS,
    )
    url = reverse("users_bookings")

    client_b = APIClient()
    client_b.force_authenticate(user=user_b)

    client_a = APIClient()
    client_a.force_authenticate(user=user_a)

    response_b = client_b.get(url)
    response_a = client_a.get(url)

    assert response_b.status_code == 200
    assert response_b.data["count"] == 0
    assert response_a.status_code == 200
    assert response_a.data["count"] == 1


@pytest.mark.django_db
def test_happy_path():
    User = get_user_model()
    user = User.objects.create_user(username="maks", password="13131313")
    resource = Resource.objects.create(
        name="Conference Room 1",
        slug="conferenceroom-1",
        description="A small room for 6 people",
        is_active=True,
    )
    data = {
        "resource": "conferenceroom-1",
        "start_time": timezone.now() + timedelta(hours=1),
        "end_time": timezone.now() + timedelta(hours=2),
    }
    client = APIClient()
    url = reverse("users_bookings")

    client.force_authenticate(user=user)
    response = client.post(url, data=data, format="json")

    assert response.status_code == 201
    assert Booking.objects.count() == 1


@pytest.mark.django_db
def test_booking_overlap():
    User = get_user_model()
    user = User.objects.create_user(username="maks", password="13131313")
    resource = Resource.objects.create(
        name="Conference Room 1",
        slug="conferenceroom-1",
        description="A small room for 6 people",
        is_active=True,
    )
    booking = Booking.objects.create(
        resource=resource,
        user=user,
        start_time=timezone.now() + timedelta(hours=1),
        end_time=(timezone.now() + timedelta(hours=2)),
        status=Booking.ACTIVE_STATUS,
    )
    client = APIClient()
    url = reverse("users_bookings")
    data = {
        "resource": "conferenceroom-1",
        "start_time": timezone.now() + timedelta(hours=1),
        "end_time": timezone.now() + timedelta(hours=2),
    }

    client.force_authenticate(user)
    response = client.post(url, data=data, format="json")

    assert response.status_code == 400
    assert Booking.objects.count() == 1


@pytest.mark.django_db
def test_end_time_lt_start_time():
    User = get_user_model()
    user = User.objects.create_user(username="maks", password="13131313")
    resource = Resource.objects.create(
        name="Conference Room 1",
        slug="conferenceroom-1",
        description="A small room for 6 people",
        is_active=True,
    )
    client = APIClient()
    url = reverse("users_bookings")
    data = {
        "resource": "conferenceroom-1",
        "start_time": timezone.now() + timedelta(hours=2),
        "end_time": timezone.now() + timedelta(hours=1),
    }

    client.force_authenticate(user)
    response = client.post(url, data=data, format="json")

    assert response.status_code == 400
    assert Booking.objects.count() == 0


@pytest.mark.django_db
def test_anonymous_user():
    client = APIClient()
    url = reverse("users_bookings")
    resource = Resource.objects.create(
        name="Conference Room 1",
        slug="conferenceroom-1",
        description="A small room for 6 people",
        is_active=True,
    )
    data = {
        "resource": "conferenceroom-1",
        "start_time": timezone.now() + timedelta(hours=1),
        "end_time": timezone.now() + timedelta(hours=2),
    }

    response = client.post(url, data=data, format="json")

    assert response.status_code == 401
    assert Booking.objects.count() == 0


@pytest.mark.django_db
def test_cancel_booking_by_owner():
    client = APIClient()
    User = get_user_model()
    user = User.objects.create_user(username="maks", password="12345")
    resource = Resource.objects.create(
        name="Conference Room 1",
        slug="conferenceroom-1",
        description="A small room for 6 people",
        is_active=True,
    )
    booking = Booking.objects.create(
        resource=resource,
        user=user,
        start_time=timezone.now() + timedelta(hours=1),
        end_time=(timezone.now() + timedelta(hours=2)),
        status=Booking.ACTIVE_STATUS,
    )
    url = reverse("cancel_booking", kwargs={"booking_id": booking.id})

    client.force_authenticate(user=user)
    response = client.post(url)

    assert response.status_code == 200

    booking.refresh_from_db()

    assert booking.status == Booking.CANCELLED_STATUS


@pytest.mark.django_db
def test_cancel_booking_by_other():
    owner = APIClient()
    other = APIClient()

    User = get_user_model()

    user_owner = User.objects.create_user(username="owner", password="owner123")
    user_other = User.objects.create_user(username="other", password="other456")

    resource = Resource.objects.create(
        name="Conference Room 1",
        slug="conferenceroom-1",
        description="A small room for 6 people",
        is_active=True,
    )
    booking = Booking.objects.create(
        resource=resource,
        user=user_owner,
        start_time=timezone.now() + timedelta(hours=1),
        end_time=(timezone.now() + timedelta(hours=2)),
        status=Booking.ACTIVE_STATUS,
    )
    url = reverse("cancel_booking", kwargs={"booking_id": booking.id})

    owner.force_authenticate(user=user_owner)
    other.force_authenticate(user=user_other)

    response = other.post(url)

    assert response.status_code == 403

    booking.refresh_from_db()

    assert booking.status == Booking.ACTIVE_STATUS


@pytest.mark.django_db
def test_cancel_olready_canceled_booking():
    client = APIClient()
    User = get_user_model()
    user = User.objects.create_user(username="maks", password="12345")
    resource = Resource.objects.create(
        name="Conference Room 1",
        slug="conferenceroom-1",
        description="A small room for 6 people",
        is_active=True,
    )
    booking = Booking.objects.create(
        resource=resource,
        user=user,
        start_time=timezone.now() + timedelta(hours=1),
        end_time=(timezone.now() + timedelta(hours=2)),
        status=Booking.CANCELLED_STATUS,
    )
    url = reverse("cancel_booking", kwargs={"booking_id": booking.id})

    client.force_authenticate(user=user)
    response = client.post(url)

    assert response.status_code == 400

    booking.refresh_from_db()

    assert booking.status == Booking.CANCELLED_STATUS
