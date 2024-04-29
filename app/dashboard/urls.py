"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,
    include,
)

from rest_framework.routers import DefaultRouter

from dashboard import views


router = DefaultRouter()
#auto generated endpoints from the view
router.register('dashboards', views.DashboardViewSet)
router.register('tags', views.TagViewSet)

app_name = 'dashboard'

urlpatterns = [
    #include the generated urls
    path('', include(router.urls)),
]