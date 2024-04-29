
"""
Tests for dashboard APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
#The APIClient class supports the same request interface as Django's standard Client class.
#This means that the standard .get(), .post(), .put(), .patch(), .delete(), .head() and .options() methods are all available.
from rest_framework.test import APIClient


from core.models import (
    Ingredient,
    Dashboard,
    Tag,
)


from dashboard.serializers import (
    DashboardSerializer,
    DashboardDetailSerializer,
)
#get url from the name of the view
#Because the urls for dashboard is generated with DefaultRouter
#dashboard-list reverses to dashboard/dashbords
#it would be possible to do dastboard-detail for id single value based endpoint
DASHBOARD_URL = reverse('dashboard:dashboard-list')

def detail_url(dashboard_id):
    #url generated from view
    """Create and return a dashboard detail URL."""
    return reverse('dashboard:dashboard-detail', args=[dashboard_id])


def create_dashboard(user, **params):
    """Create and return a sample dashboard."""
    defaults = {
        'gridConfig': 'string',
        'description': 'Sample description',

    }
    defaults.update(params)

    dashboard = Dashboard.objects.create(user=user, **defaults)
    return dashboard


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)



class PublicDashboardAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(DASHBOARD_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatedashboardApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        # self.user = get_user_model().objects.create_user(
        #     'user@example.com',
        #     'testpass123',
        # )
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user)

    def test_retrieve_strategies(self):
        """Test retrieving a list of dashboards."""
        create_dashboard(user=self.user)
        create_dashboard(user=self.user)

        res = self.client.get(DASHBOARD_URL)

        strategies = Dashboard.objects.all().order_by('-id')
        serializer = DashboardSerializer(strategies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_dashboard_list_limited_to_user(self):
        """Only returns the dashboard from the authenticated user."""
        # other_user = get_user_model().objects.create_user(
        #     'other@example.com',
        #     'password123',
        # )
        other_user = create_user(email='other@example.com', password='test123')
        create_dashboard(user=other_user)
        create_dashboard(user=self.user)

        res = self.client.get(DASHBOARD_URL)
        #finds strategies from authenticated user
        strategies = Dashboard.objects.filter(user=self.user)
        serializer = DashboardSerializer(strategies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_dashboard_detail(self):
        """Test get dashboard detail."""
        dashboard = create_dashboard(user=self.user)

        url = detail_url(dashboard.id)
        res = self.client.get(url)

        serializer = DashboardDetailSerializer(dashboard)
        self.assertEqual(res.data, serializer.data)

    def test_create_dashboard(self):
        """Test creating a dashboard."""
        payload = {
            'gridConfig': 'string'
        }
        print(DASHBOARD_URL)
        res = self.client.post(DASHBOARD_URL, payload)
        print(res,"res")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        dashboard = Dashboard.objects.get(id=res.data['id'])
        #getattr allows us to get attribute using a variable attribute name
        #https://docs.python.org/3/library/functions.html#getattr
        for k, v in payload.items():
            self.assertEqual(getattr(dashboard, k), v)
            print(getattr(dashboard, k), v)
        self.assertEqual(dashboard.user, self.user)


#     def test_partial_update(self):
#         """Test partial update of a dashboard."""
#         original_link = 'https://example.com/dashboard.pdf'
#         dashboard = create_dashboard(
#             user=self.user,
#             title='Sample dashboard title',
#             link=original_link,
#         )

#         payload = {'title': 'New dashboard title'}
#         url = detail_url(dashboard.id)
#         res = self.client.patch(url, payload)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         dashboard.refresh_from_db()
#         self.assertEqual(dashboard.title, payload['title'])
#         self.assertEqual(dashboard.link, original_link)
#         self.assertEqual(dashboard.user, self.user)

#     def test_full_update(self):
#         """Test full update of dashboard."""
#         dashboard = create_dashboard(
#             user=self.user,
#             title='Sample dashboard title',
#             link='https://exmaple.com/dashboard.pdf',
#             description='Sample dashboard description.',
#         )

#         payload = {
#             'title': 'New dashboard title',
#             'link': 'https://example.com/new-dashboard.pdf',
#             'description': 'New dashboard description',
#             'time_minutes': 10,
#             'price': Decimal('2.50'),
#         }
#         url = detail_url(dashboard.id)
#         res = self.client.put(url, payload)

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         dashboard.refresh_from_db()
#         for k, v in payload.items():
#             self.assertEqual(getattr(dashboard, k), v)
#         self.assertEqual(dashboard.user, self.user)
