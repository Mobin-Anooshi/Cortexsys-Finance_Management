from django.urls import path
from . import views
from rest_framework import routers



app_name = "transactions"
urlpatterns = []

router = routers.SimpleRouter()
router.register('',views.TransactionAPIView)
urlpatterns += router.urls