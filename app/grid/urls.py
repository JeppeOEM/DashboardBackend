"""
URL mappings for the strategy app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from grid import views


router = DefaultRouter()
#auto generated endpoints from the view
router.register('grids', views.GridViewSet)

app_name = 'grid'

urlpatterns = [
    #include the generated urls
    path('', include(router.urls)),
]