from django.urls import path, include

from .views import test_api

urlpatterns = [
    path("api/test/", test_api)
]
