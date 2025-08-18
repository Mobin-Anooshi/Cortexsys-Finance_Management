from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView

app_name = "accounts"
urlpatterns = [
    path('register/',views.UserRegisterAPIView.as_view()),
    # path('login/',views.UserLoginAPIView.as_view())
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
