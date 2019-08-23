from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from timetracker.api.views import EmployeeViewSet
from timetracker.api.views import get_team_work_percent
from rest_framework.authtoken.views import obtain_auth_token

api_router = DefaultRouter()
api_router.register(r'employees', EmployeeViewSet, 'employees')

urlpatterns = [
    url(r'^v1/', include(api_router.urls)),
    url(r'^v1/team-work', get_team_work_percent),
    url(r'^v1/auth', obtain_auth_token)

]
