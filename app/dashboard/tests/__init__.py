
"""
Tests for strategy APIs.
"""
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Ingredient,
    Dashboard,
    Tag,
)

from strategy.serializers import (
    StrategySerializer,
    StrategyDetailSerializer,
)

DASHBOARD_URL = reverse('dashboard:strategy-list')