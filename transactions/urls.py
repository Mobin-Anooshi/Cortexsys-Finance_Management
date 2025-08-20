"""
URL configuration for the Transactions app.

Registers TransactionAPIView with a SimpleRouter to provide RESTful endpoints.
Mounted at /api/transactions/ in the main urls.py.
"""

from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "transactions"
router = routers.SimpleRouter()
router.register('', views.TransactionAPIView, basename='transaction')

urlpatterns = router.urls