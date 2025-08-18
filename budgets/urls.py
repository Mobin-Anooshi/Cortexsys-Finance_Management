from django.urls import path
from . import views
from rest_framework import routers

app_name = "budgets"
urlpatterns = []

router = routers.SimpleRouter()
router.register('',views.BudgetAPIView)
urlpatterns += router.urls