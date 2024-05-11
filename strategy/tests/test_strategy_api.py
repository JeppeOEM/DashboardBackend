
"""
Tests for strategy APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from core.models import Indicator, Strategy, Tag
from strategy.serializers import StrategyDetailSerializer, StrategySerializer

# get url from the name of the view
# Because the urls for strategy is generated with DefaultRouter
# strategy-list reverses to strategy/strategies
# it would be possible to do strategy-detail for id single value based endpoint
STRATEGY_URL = reverse('strategy:strategy-list')


def detail_url(strategy_id):
    """Create and return a strategy detail URL."""
    return reverse('strategy:strategy-detail', args=[strategy_id])


def create_strategy(user, **params):
    """Create and return a sample strategy."""
    defaults = {
        'title': 'Sample strategy title',
        'time_minutes': 22,
        'price': Decimal('5.25'),
        'description': 'Sample description',
    }
    defaults.update(params)

    strategy = Strategy.objects.create(user=user, **defaults)
    return strategy


def create_user(**params):
    """Create and return a new user."""
    return get_user_model().objects.create_user(**params)


class PublicStrategyAPITests(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test auth is required to call API."""
        res = self.client.get(STRATEGY_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateStrategyApiTests(TestCase):
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
        """Test retrieving a list of strategies."""
        create_strategy(user=self.user)
        create_strategy(user=self.user)

        res = self.client.get(STRATEGY_URL)

        strategies = Strategy.objects.all().order_by('-id')
        serializer = StrategySerializer(strategies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_strategy_list_limited_to_user(self):
        """Test list of strategies is limited to authenticated user."""
        # other_user = get_user_model().objects.create_user(
        #     'other@example.com',
        #     'password123',
        # )
        other_user = create_user(email='other@example.com', password='test123')
        create_strategy(user=other_user)
        create_strategy(user=self.user)

        res = self.client.get(STRATEGY_URL)

        strategies = Strategy.objects.filter(user=self.user)
        serializer = StrategySerializer(strategies, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_strategy_detail(self):
        """Test get strategy detail."""
        strategy = create_strategy(user=self.user)

        url = detail_url(strategy.id)
        res = self.client.get(url)

        serializer = StrategyDetailSerializer(strategy)
        self.assertEqual(res.data, serializer.data)

    def test_create_strategy(self):
        """Test creating a strategy."""
        payload = {
            'title': 'Sample strategy',
            'time_minutes': 30,
            'price': Decimal('5.99'),
        }
        res = self.client.post(STRATEGY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        strategy = Strategy.objects.get(id=res.data['id'])
        # getattr allows us to get attribute using a variable attribute name
        # https://docs.python.org/3/library/functions.html#getattr
        for k, v in payload.items():
            self.assertEqual(getattr(strategy, k), v)
        self.assertEqual(strategy.user, self.user)

    def test_partial_update(self):
        """Test partial update of a strategy."""
        original_link = 'https://example.com/strategy.pdf'
        strategy = create_strategy(
            user=self.user,
            title='Sample strategy title',
            link=original_link,
        )

        payload = {'title': 'New strategy title'}
        url = detail_url(strategy.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        strategy.refresh_from_db()
        self.assertEqual(strategy.title, payload['title'])
        self.assertEqual(strategy.link, original_link)
        self.assertEqual(strategy.user, self.user)

    def test_full_update(self):
        """Test full update of strategy."""
        strategy = create_strategy(
            user=self.user,
            title='Sample strategy title',
            link='https://exmaple.com/strategy.pdf',
            description='Sample strategy description.',
        )

        payload = {
            'title': 'New strategy title',
            'link': 'https://example.com/new-strategy.pdf',
            'description': 'New strategy description',
            'time_minutes': 10,
            'price': Decimal('2.50'),
        }
        url = detail_url(strategy.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        strategy.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(strategy, k), v)
        self.assertEqual(strategy.user, self.user)

    def test_update_user_returns_error(self):
        """Test changing the strategy user results in an error."""
        new_user = create_user(email='user2@example.com', password='test123')
        strategy = create_strategy(user=self.user)

        payload = {'user': new_user.id}
        url = detail_url(strategy.id)
        self.client.patch(url, payload)

        strategy.refresh_from_db()
        self.assertEqual(strategy.user, self.user)

    def test_delete_strategy(self):
        """Test deleting a strategy successful."""
        strategy = create_strategy(user=self.user)

        url = detail_url(strategy.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Strategy.objects.filter(id=strategy.id).exists())

    def test_strategy_other_users_strategy_error(self):
        """Test trying to delete another users strategy gives error."""
        new_user = create_user(email='user2@example.com', password='test123')
        strategy = create_strategy(user=new_user)

        url = detail_url(strategy.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Strategy.objects.filter(id=strategy.id).exists())

    def test_create_strategy_with_new_tags(self):
        """Test creating a strategy with new tags."""
        payload = {
            'title': 'Thai Prawn Curry',
            'time_minutes': 30,
            'price': Decimal('2.50'),
            'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
        }
        res = self.client.post(STRATEGY_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        strategies = Strategy.objects.filter(user=self.user)
        self.assertEqual(strategies.count(), 1)
        strategy = strategies[0]
        self.assertEqual(strategy.tags.count(), 2)
        for tag in payload['tags']:
            exists = strategy.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_strategy_with_existing_tags(self):
        """Test creating a strategy with existing tag."""
        tag_indian = Tag.objects.create(user=self.user, name='Indian')
        payload = {
            'title': 'Pongal',
            'time_minutes': 60,
            'price': Decimal('4.50'),
            'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}],
        }
        res = self.client.post(STRATEGY_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        strategies = Strategy.objects.filter(user=self.user)
        self.assertEqual(strategies.count(), 1)
        strategy = strategies[0]
        self.assertEqual(strategy.tags.count(), 2)
        self.assertIn(tag_indian, strategy.tags.all())
        for tag in payload['tags']:
            exists = strategy.tags.filter(
                name=tag['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test create tag when updating a strategy."""
        strategy = create_strategy(user=self.user)

        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(strategy.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(user=self.user, name='Lunch')
        self.assertIn(new_tag, strategy.tags.all())

    def test_update_strategy_assign_tag(self):
        """Test assigning an existing tag when updating a strategy."""
        tag_breakfast = Tag.objects.create(user=self.user, name='Breakfast')
        strategy = create_strategy(user=self.user)
        strategy.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(user=self.user, name='Lunch')
        payload = {'tags': [{'name': 'Lunch'}]}
        url = detail_url(strategy.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag_lunch, strategy.tags.all())
        self.assertNotIn(tag_breakfast, strategy.tags.all())

    def test_clear_strategy_tags(self):
        """Test clearing a strategies tags."""
        tag = Tag.objects.create(user=self.user, name='Dessert')
        strategy = create_strategy(user=self.user)
        strategy.tags.add(tag)

        payload = {'tags': []}
        url = detail_url(strategy.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(strategy.tags.count(), 0)

    def test_create_strategy_with_new_indicators(self):
        """Test creating a strategy with new indicators."""
        payload = {
            'title': 'Cauliflower Tacos',
            'time_minutes': 60,
            'price': Decimal('4.30'),
            'indicators': [{'name': 'Cauliflower'}, {'name': 'Salt'}],
        }
        res = self.client.post(STRATEGY_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        strategies = Strategy.objects.filter(user=self.user)
        self.assertEqual(strategies.count(), 1)
        strategy = strategies[0]
        self.assertEqual(strategy.indicators.count(), 2)
        for indicator in payload['indicators']:
            exists = strategy.indicators.filter(
                name=indicator['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_strategy_with_existing_indicator(self):
        """Test creating a new strategy with existing indicator."""
        indicator = Indicator.objects.create(user=self.user, name='Lemon')
        payload = {
            'title': 'Vietnamese Soup',
            'time_minutes': 25,
            'price': '2.55',
            'indicators': [{'name': 'Lemon'}, {'name': 'Fish Sauce'}],
        }
        res = self.client.post(STRATEGY_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        strategies = Strategy.objects.filter(user=self.user)
        self.assertEqual(strategies.count(), 1)
        strategy = strategies[0]
        self.assertEqual(strategy.indicators.count(), 2)
        self.assertIn(indicator, strategy.indicators.all())
        for indicator in payload['indicators']:
            exists = strategy.indicators.filter(
                name=indicator['name'],
                user=self.user,
            ).exists()
            self.assertTrue(exists)

    def test_create_indicator_on_update(self):
        """Test creating an indicator when updating a strategy."""
        strategy = create_strategy(user=self.user)

        payload = {'indicators': [{'name': 'Limes'}]}
        url = detail_url(strategy.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_indicator = Indicator.objects.get(user=self.user, name='Limes')
        self.assertIn(new_indicator, strategy.indicators.all())

    def test_update_strategy_assign_indicator(self):
        """Test assigning an existing indicator when updating a strategy."""
        indicator1 = Indicator.objects.create(user=self.user, name='Pepper')
        strategy = create_strategy(user=self.user)
        strategy.indicators.add(indicator1)

        indicator2 = Indicator.objects.create(user=self.user, name='Chili')
        payload = {'indicators': [{'name': 'Chili'}]}
        url = detail_url(strategy.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(indicator2, strategy.indicators.all())
        self.assertNotIn(indicator1, strategy.indicators.all())

    def test_clear_strategy_indicators(self):
        """Test clearing a strategies indicators."""
        indicator = Indicator.objects.create(user=self.user, name='Garlic')
        strategy = create_strategy(user=self.user)
        strategy.indicators.add(indicator)

        payload = {'indicators': []}
        url = detail_url(strategy.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(strategy.indicators.count(), 0)


#########


# """
# Tests for strategy APIs.
# """
# from decimal import Decimal
# from django.contrib.auth import get_user_model
# from django.test import TestCase
# from django.urls import reverse
# from rest_framework import status
# from rest_framework.test import APIClient

# from core.models import Strategy
# from core.models import (
#     Strategy,
#     Tag,
# )

# from strategy.serializers import (
#     StrategySerializer,
#     StrategyDetailSerializer,
# )
# STRATEGY_URL = reverse('strategy:strategy-list')
# def detail_url(strategy_id):
#     """Create and return a strategy detail URL."""
#     return reverse('strategy:strategy-detail', args=[strategy_id])
# def create_strategy(user, **params):
#     """Create and return a sample strategy."""
#     defaults = {
#         'title': 'Sample strategy title',
#         'time_minutes': 22,
#         'price': Decimal('5.25'),
#         'description': 'Sample description',
#         'link': 'http://example.com/strategy.pdf',
#     }
#     defaults.update(params)
#     strategy = Strategy.objects.create(user=user, **defaults)
#     return strategy
# def create_user(**params):
#     """Create and return a new user."""
#     return get_user_model().objects.create_user(**params)
# class PublicStrategyAPITests(TestCase):
#     """Test unauthenticated API requests."""
#     def setUp(self):
#         self.client = APIClient()
#     def test_auth_required(self):
#         """Test auth is required to call API."""
#         res = self.client.get(STRATEGY_URL)
#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
# class PrivateStrategyApiTests(TestCase):
#     """Test authenticated API requests."""
#     def setUp(self):
#         self.client = APIClient()
#         self.user = create_user(email='user@example.com', password='test123')
#         self.client.force_authenticate(self.user)
#     def test_retrieve_strategies(self):
#         """Test retrieving a list of strategies."""
#         create_strategy(user=self.user)
#         create_strategy(user=self.user)
#         res = self.client.get(STRATEGY_URL)
#         strategies = Strategy.objects.all().order_by('-id')
#         serializer = StrategySerializer(strategies, many=True)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, serializer.data)
#     def test_strategy_list_limited_to_user(self):
#         """Test list of strategies is limited to authenticated user."""
#         other_user = create_user(email='other@example.com', password='test123')
#         create_strategy(user=other_user)
#         create_strategy(user=self.user)
#         res = self.client.get(STRATEGY_URL)
#         strategies = Strategy.objects.filter(user=self.user)
#         serializer = StrategySerializer(strategies, many=True)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         self.assertEqual(res.data, serializer.data)
#     def test_get_strategy_detail(self):
#         """Test get strategy detail."""
#         strategy = create_strategy(user=self.user)
#         url = detail_url(strategy.id)
#         res = self.client.get(url)
#         serializer = StrategyDetailSerializer(strategy)
#         self.assertEqual(res.data, serializer.data)
#     def test_create_strategy(self):
#         """Test creating a strategy."""
#         payload = {
#             'title': 'Sample strategy',
#             'time_minutes': 30,
#             'price': Decimal('5.99'),
#         }
#         res = self.client.post(STRATEGY_URL, payload)
#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         strategy = Strategy.objects.get(id=res.data['id'])
#         for k, v in payload.items():
#             self.assertEqual(getattr(strategy, k), v)
#         self.assertEqual(strategy.user, self.user)
#     def test_partial_update(self):
#         """Test partial update of a strategy."""
#         original_link = 'https://example.com/strategy.pdf'
#         strategy = create_strategy(
#             user=self.user,
#             title='Sample strategy title',
#             link=original_link,
#         )
#         payload = {'title': 'New strategy title'}
#         url = detail_url(strategy.id)
#         res = self.client.patch(url, payload)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         strategy.refresh_from_db()
#         self.assertEqual(strategy.title, payload['title'])
#         self.assertEqual(strategy.link, original_link)
#         self.assertEqual(strategy.user, self.user)
#     def test_full_update(self):
#         """Test full update of strategy."""
#         strategy = create_strategy(
#             user=self.user,
#             title='Sample strategy title',
#             link='https://exmaple.com/strategy.pdf',
#             description='Sample strategy description.',
#         )
#         payload = {
#             'title': 'New strategy title',
#             'link': 'https://example.com/new-strategy.pdf',
#             'description': 'New strategy description',
#             'time_minutes': 10,
#             'price': Decimal('2.50'),
#         }
#         url = detail_url(strategy.id)
#         res = self.client.put(url, payload)
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         strategy.refresh_from_db()
#         for k, v in payload.items():
#             self.assertEqual(getattr(strategy, k), v)
#         self.assertEqual(strategy.user, self.user)
#     def test_update_user_returns_error(self):
#         """Test changing the strategy user results in an error."""
#         new_user = create_user(email='user2@example.com', password='test123')
#         strategy = create_strategy(user=self.user)
#         payload = {'user': new_user.id}
#         url = detail_url(strategy.id)
#         self.client.patch(url, payload)
#         strategy.refresh_from_db()
#         self.assertEqual(strategy.user, self.user)
#     def test_delete_strategy(self):
#         """Test deleting a strategy successful."""
#         strategy = create_strategy(user=self.user)
#         url = detail_url(strategy.id)
#         res = self.client.delete(url)
#         self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertFalse(Strategy.objects.filter(id=strategy.id).exists())
#     def test_strategy_other_users_strategy_error(self):
#         """Test trying to delete another users strategy gives error."""
#         new_user = create_user(email='user2@example.com', password='test123')
#         strategy = create_strategy(user=new_user)
#         url = detail_url(strategy.id)
#         res = self.client.delete(url)

#         self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
#         self.assertTrue(Strategy.objects.filter(id=strategy.id).exists())

#     def test_create_strategy_with_new_tags(self):
#         """Test creating a strategy with new tags."""
#         payload = {
#             'title': 'Thai Prawn Curry',
#             'time_minutes': 30,
#             'price': Decimal('2.50'),
#             'tags': [{'name': 'Thai'}, {'name': 'Dinner'}],
#         }
#         res = self.client.post(STRATEGY_URL, payload, format='json')

#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         strategies = Strategy.objects.filter(user=self.user)
#         self.assertEqual(strategies.count(), 1)
#         strategy = strategies[0]
#         self.assertEqual(strategy.tags.count(), 2)
#         for tag in payload['tags']:
#             exists = strategy.tags.filter(
#                 name=tag['name'],
#                 user=self.user,
#             ).exists()
#             self.assertTrue(exists)

#     def test_create_strategy_with_existing_tags(self):
#         """Test creating a strategy with existing tag."""
#         tag_indian = Tag.objects.create(user=self.user, name='Indian')
#         payload = {
#             'title': 'Pongal',
#             'time_minutes': 60,
#             'price': Decimal('4.50'),
#             'tags': [{'name': 'Indian'}, {'name': 'Breakfast'}],
#         }
#         res = self.client.post(STRATEGY_URL, payload, format='json')

#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         strategies = Strategy.objects.filter(user=self.user)
#         self.assertEqual(strategies.count(), 1)
#         strategy = strategies[0]
#         self.assertEqual(strategy.tags.count(), 2)
#         self.assertIn(tag_indian, strategy.tags.all())
#         for tag in payload['tags']:
#             exists = strategy.tags.filter(
#                 name=tag['name'],
#                 user=self.user,
#             ).exists()
#             self.assertTrue(exists)
