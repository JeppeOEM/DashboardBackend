"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from strategy import views


router = DefaultRouter()
#auto generated endpoints from the view
router.register('strategies', views.RecipeViewSet)

app_name = 'strategy'

urlpatterns = [
    #include the generated urls
    path('', include(router.urls)),
]