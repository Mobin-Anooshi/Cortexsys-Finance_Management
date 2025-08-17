from django.urls import path
from . import views


app_name = "accounts"
urlpatterns = [
    path('register/',views.UserRegisterAPIView.as_view()),
    path('login/',views.UserLoginAPIView.as_view())

]
