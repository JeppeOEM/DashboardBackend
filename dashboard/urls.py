
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from dashboard import views

router = DefaultRouter()
# auto generated endpoints from the view
router.register('dashboards', views.DashboardViewSet)

app_name = 'dashboard'

urlpatterns = [
    # include the generated urls
    path('', include(router.urls)),
]
