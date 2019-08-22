from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter
from timetracker.api.views import EmployeeViewSet
from timetracker.api.views import CheckingViewSet
from timetracker.api.views import VacationViewSet

api_router = DefaultRouter()
api_router.register(r'users', EmployeeViewSet, 'users')
api_router.register(r'checking', CheckingViewSet, 'checking')
api_router.register(r'vacations', VacationViewSet, 'vacations')

urlpatterns = [
    url(r'^v1/', include(api_router.urls)),
    url(r'^v1/auth', obtain_jwt_token)

]
