
from django.conf.urls import url, include
from rest_framework_jwt.views import obtain_jwt_token
from rest_framework.routers import DefaultRouter
from timetracker.api.views import UserViewSet

api_router = DefaultRouter()
api_router.register(r'users', UserViewSet, 'users')
urlpatterns = [
    url(r'^v1/', include(api_router.urls)),
    url(r'^v1/auth', obtain_jwt_token)

]
