
"""
Tests for grid APIs.
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
    Grid,
)


from grid.serializers import (
    GridSerializer
)
#get url from the name of the view
#Because the urls for grid is generated with DefaultRouter
#grid-list reverses to grid/dashbords
#it would be possible to do dastboard-detail for id single value based endpoint
GRID_URL = reverse('grid:grid-list')

def detail_url(grid_id):
    #url generated from view
    """Create and return a grid detail URL."""
    return reverse('grid:grid-detail', args=[grid_id])


def create_grid(user, **params):
    """Create and return a sample grid."""
    defaults = {
        'gridConfig': 'string',
        'description': 'Sample description',

    }
    defaults.update(params)

    grid = Grid.objects.create(user=user, **defaults)
    return grid


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)



class PublicGridAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(GRID_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateGridApiTests(TestCase):
    """Test authenticated API requests."""

    def setUp(self):
        self.client = APIClient()
        # self.user = get_user_model().objects.create_user(
        #     'user@example.com',
        #     'testpass123',
        # )
        self.user = create_user(email='user@example.com', password='test123')
        self.client.force_authenticate(self.user)

    def test_retrieve_grids(self):
        """Test retrieving a list of grids."""
        create_grid(user=self.user)
        create_grid(user=self.user)

        res = self.client.get(GRID_URL)

        strategies = Grid.objects.all().order_by('-id')
        serializer = GridSerializer(strategies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_grid_list_limited_to_user(self):
        """Only returns the grid from the authenticated user."""
        # other_user = get_user_model().objects.create_user(
        #     'other@example.com',
        #     'password123',
        # )
        other_user = create_user(email='other@example.com', password='test123')
        create_grid(user=other_user)
        create_grid(user=self.user)

        res = self.client.get(GRID_URL)
        #finds strategies from authenticated user
        strategies = Grid.objects.filter(user=self.user)
        serializer = GridSerializer(strategies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)



    def test_create_grid(self):
        """Test creating a grid."""
        payload = {
            'gridConfig': 'string'
        }
        print(GRID_URL)
        res = self.client.post(GRID_URL, payload)
        print(res,"res")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        grid = Grid.objects.get(id=res.data['id'])
        #getattr allows us to get attribute using a variable attribute name
        #https://docs.python.org/3/library/functions.html#getattr
        for k, v in payload.items():
            self.assertEqual(getattr(grid, k), v)
            print(getattr(grid, k), v)
        self.assertEqual(grid.user, self.user)


    def test_partial_update(self):
        """Test partial update of a grid."""
        original_description = 'olololololol'
        grid = create_grid(
            user=self.user,
            gridConfig='Sample grid gridConfig',
            link=original_description,
        )
        payload = {'gridConfig': 'New grid gridConfig'}
        url = detail_url(grid.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        grid.refresh_from_db()
        self.assertEqual(grid.gridConfig, payload['gridConfig'])
        self.assertEqual(grid.link, original_description)
        self.assertEqual(grid.user, self.user)

    def test_full_update(self):
        """Test full update of grid."""
        grid = create_grid(
            user=self.user,
            gridConfig='Sample grid gridConfig',
            description='Sample grid description.',
        )

        payload = {
            'gridConfig': 'New grid gridConfig',
            'description': 'New grid description',
        }
        url = detail_url(grid.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        grid.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(grid, k), v)
        self.assertEqual(grid.user, self.user)
