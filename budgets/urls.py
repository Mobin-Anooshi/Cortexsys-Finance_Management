"""
URL configuration for the Budgets app.

Registers BudgetAPIView with a SimpleRouter to provide RESTful endpoints.
Mounted at /api/budgets/ in the main urls.py.
"""

from django.urls import path, include
from rest_framework import routers
from . import views

app_name = "budgets"
router = routers.SimpleRouter()
router.register('', views.BudgetAPIView, basename='budget')

urlpatterns = router.urls