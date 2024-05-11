"""
Tests for the indicators API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Indicator
from strategy.serializers import IndicatorSerializer

STRATEGY_URL = reverse('strategy:indicator-list')


def detail_url(indicator_id):
    """Create and return an indicator detail URL."""
    return reverse('strategy:indicator-detail', args=[indicator_id])


def create_user(email='user@example.com', password='testpass123'):
    """Create and return user."""
    return get_user_model().objects.create_user(email=email, password=password)


class PublicIndicatorsApiTests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required for retrieving indicators."""
        res = self.client.get(STRATEGY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIndicatorsApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_indicators(self):
        """Test retrieving a list of indicators."""
        Indicator.objects.create(user=self.user, name='Kale')
        Indicator.objects.create(user=self.user, name='Vanilla')

        res = self.client.get(STRATEGY_URL)

        indicators = Indicator.objects.all().order_by('-name')
        serializer = IndicatorSerializer(indicators, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_indicators_limited_to_user(self):
        """Test list of indicators is limited to authenticated user."""
        user2 = create_user(email='user2@example.com')
        Indicator.objects.create(user=user2, name='Salt')
        indicator = Indicator.objects.create(user=self.user, name='Pepper')

        res = self.client.get(STRATEGY_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], indicator.name)
        self.assertEqual(res.data[0]['id'], indicator.id)

    def test_update_indicator(self):
        """Test updating an indicator."""
        indicator = Indicator.objects.create(user=self.user, name='Cilantro')

        payload = {'name': 'Coriander'}
        url = detail_url(indicator.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        indicator.refresh_from_db()
        self.assertEqual(indicator.name, payload['name'])

    def test_delete_indicator(self):
        """Test deleting an indicator."""
        indicator = Indicator.objects.create(user=self.user, name='Lettuce')

        url = detail_url(indicator.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        indicators = Indicator.objects.filter(user=self.user)
        self.assertFalse(indicators.exists())
