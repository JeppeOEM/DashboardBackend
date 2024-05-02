"""
URL mappings for the strategy app.
"""
from django.urls import (
    path,
    include,
)
#DefaultRouter in your urls.py, it automatically generates a set of URLs for each viewset
#you register with it. These generated URLs are based on the names of the viewsets and
#the actions they support.

from rest_framework.routers import DefaultRouter

from strategy import views


router = DefaultRouter()
#auto generated endpoints from the view
router.register('strategies', views.StrategyViewSet)
router.register('tags', views.TagViewSet)
router.register('indicators', views.IndicatorViewSet)
router.register('coins', views.CoinViewSet)
router.register('bases', views.BaseViewSet)

app_name = 'strategy'

urlpatterns = [
    #include the generated urls
    path('', include(router.urls)),
]