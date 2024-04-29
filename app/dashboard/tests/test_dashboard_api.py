
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
            'gridConfig': 'string',
            'description': "string"
        }
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

#     def test_update_user_returns_error(self):
#         """Test changing the dashboard user results in an error."""
#         new_user = create_user(email='user2@example.com', password='test123')
#         dashboard = create_dashboard(user=self.user)

#         payload = {'user': new_user.id}
#         url = detail_url(dashboard.id)
#         self.client.patch(url, payload)

#         dashboard.refresh_from_db()
#         self.assertEqual(dashboard.user, self.user)

#     def test_delete_dashboard(self):
#         """Test deleting a dashboard successful."""
#         dashboard = create_dashboard(user=self.user)

#         url = detail_url(dashboard.id)
#         res = self.client.delete(url)

#         self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertFalse(dashboard.objects.filter(id=dashboard.id).exists())

#     def test_dashboard_other_users_dashboard_error(self):
#         """Test trying to delete another users dashboard gives error."""
#         new_user = create_user(email='user2@example.com', password='test123')
#         dashboard = create_dashboard(user=new_user)

#         url = detail_url(dashboard.id)
#         res = self.client.delete(url)

#         self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertTrue(dashboard.objects.filter(id=dashboard.id).exists())


#     def test_create_dashboard_with_new_tags(self):
#         """Test creating a dashboard with new tags."""
#         payload = {
#             'title': 'Thai Prawn Curry',
#             'time_minutes': 30,
#             'price': Decimal('2.50'),
#             'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
#         }
#         res = self.client.post(dashboard_URL, payload, format='json')

#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         strategies = dashboard.objects.filter(user=self.user)
#         self.assertEqual(strategies.count(), 1)
#         dashboard = strategies[0]
#         self.assertEqual(dashboard.tags.count(), 2)
#         for tag in payload['tags']:
#             exists = dashboard.tags.filter(
#                 name=tag['name'],
#                 user=self.user,
#             ).exists()
#             self.assertTrue(exists)


#     def test_create_dashboard_with_existing_tags(self):
#         """Test creating a dashboard with existing tag."""
#         tag_indian = Tag.objects.create(user=self.user, name='Indian')
#         payload = {
#             'title': 'Pongal',
#             'time_minutes': 60,
#             'price': Decimal('4.50'),
#             'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}],
#         }
#         res = self.client.post(dashboard_URL, payload, format='json')

#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         strategies = dashboard.objects.filter(user=self.user)
#         self.assertEqual(strategies.count(), 1)
#         dashboard = strategies[0]
#         self.assertEqual(dashboard.tags.count(), 2)
#         self.assertIn(tag_indian, dashboard.tags.all())
#         for tag in payload['tags']:
#             exists = dashboard.tags.filter(
#                 name=tag['name'],
#                 user=self.user,
#             ).exists()
#             self.assertTrue(exists)


#     def test_create_tag_on_update(self):
#         """Test create tag when updating a dashboard."""
#         dashboard = create_dashboard(user=self.user)

#         payload = {'tags': [{'name': 'Lunch'}]}
#         url = detail_url(dashboard.id)
#         res = self.client.patch(url, payload, format='json')

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         new_tag = Tag.objects.get(user=self.user, name='Lunch')
#         self.assertIn(new_tag, dashboard.tags.all())

#     def test_update_dashboard_assign_tag(self):
#         """Test assigning an existing tag when updating a dashboard."""
#         tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
#         dashboard = create_dashboard(user=self.user)
#         dashboard.tags.add(tag_breakfast)

#         tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
#         payload = {'tags': [{'name': 'Lunch'}]}
#         url = detail_url(dashboard.id)
#         res = self.client.patch(url, payload, format='json')

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertIn(tag_lunch, dashboard.tags.all())
#         self.assertNotIn(tag_breakfast, dashboard.tags.all())

#     def test_clear_dashboard_tags(self):
#         """Test clearing a strategies tags."""
#         tag = Tag.objects.create(user=self.user, name='Dessert')
#         dashboard = create_dashboard(user=self.user)
#         dashboard.tags.add(tag)

#         payload = {'tags': []}
#         url = detail_url(dashboard.id)
#         res = self.client.patch(url, payload, format='json')

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(dashboard.tags.count(), 0)




#     def test_create_dashboard_with_new_ingredients(self):
#         """Test creating a dashboard with new ingredients."""
#         payload = {
#             'title': 'Cauliflower Tacos',
#             'time_minutes': 60,
#             'price': Decimal('4.30'),
#             'ingredients': [{'name': 'Cauliflower'}, {'name': 'Salt'}],
#         }
#         res = self.client.post(dashboard_URL, payload, format='json')

#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         strategies = dashboard.objects.filter(user=self.user)
#         self.assertEqual(strategies.count(), 1)
#         dashboard = strategies[0]
#         self.assertEqual(dashboard.ingredients.count(), 2)
#         for ingredient in payload['ingredients']:
#             exists = dashboard.ingredients.filter(
#                 name=ingredient['name'],
#                 user=self.user,
#             ).exists()
#             self.assertTrue(exists)

#     def test_create_dashboard_with_existing_ingredient(self):
#         """Test creating a new dashboard with existing ingredient."""
#         ingredient = Ingredient.objects.create(user=self.user, name='Lemon')
#         payload = {
#             'title': 'Vietnamese Soup',
#             'time_minutes': 25,
#             'price': '2.55',
#             'ingredients': [{'name': 'Lemon'}, {'name': 'Fish Sauce'}],
#         }
#         res = self.client.post(dashboard_URL, payload, format='json')

#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         strategies = dashboard.objects.filter(user=self.user)
#         self.assertEqual(strategies.count(), 1)
#         dashboard = strategies[0]
#         self.assertEqual(dashboard.ingredients.count(), 2)
#         self.assertIn(ingredient, dashboard.ingredients.all())
#         for ingredient in payload['ingredients']:
#             exists = dashboard.ingredients.filter(
#                 name=ingredient['name'],
#                 user=self.user,
#             ).exists()
#             self.assertTrue(exists)

#     def test_create_ingredient_on_update(self):
#         """Test creating an ingredient when updating a dashboard."""
#         dashboard = create_dashboard(user=self.user)

#         payload = {'ingredients': [{'name': 'Limes'}]}
#         url = detail_url(dashboard.id)
#         res = self.client.patch(url, payload, format='json')

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         new_ingredient = Ingredient.objects.get(user=self.user, name='Limes')
#         self.assertIn(new_ingredient, dashboard.ingredients.all())

#     def test_update_dashboard_assign_ingredient(self):
#         """Test assigning an existing ingredient when updating a dashboard."""
#         ingredient1 = Ingredient.objects.create(user=self.user, name='Pepper')
#         dashboard = create_dashboard(user=self.user)
#         dashboard.ingredients.add(ingredient1)

#         ingredient2 = Ingredient.objects.create(user=self.user, name='Chili')
#         payload = {'ingredients': [{'name': 'Chili'}]}
#         url = detail_url(dashboard.id)
#         res = self.client.patch(url, payload, format='json')

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertIn(ingredient2, dashboard.ingredients.all())
#         self.assertNotIn(ingredient1, dashboard.ingredients.all())

#     def test_clear_dashboard_ingredients(self):
#         """Test clearing a strategies ingredients."""
#         ingredient = Ingredient.objects.create(user=self.user, name='Garlic')
#         dashboard = create_dashboard(user=self.user)
#         dashboard.ingredients.add(ingredient)

#         payload = {'ingredients': []}
#         url = detail_url(dashboard.id)
#         res = self.client.patch(url, payload, format='json')

#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(dashboard.ingredients.count(), 0)
