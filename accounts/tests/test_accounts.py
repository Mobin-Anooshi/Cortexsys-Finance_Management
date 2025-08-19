import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from accounts.managers import UserManagers
from django.contrib.auth import get_user_model


# فیکچر برای کلاینت API
@pytest.fixture
def api_client():
    return APIClient()


# فیکچر برای داده‌های کاربر
@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'Testpass123'
    }


# تست‌های قبلی (برای مرجع، تکرار نمی‌شوند)
# ... (تست‌های UserRegisterAPIView و سریالایزر)

# تست ایجاد کاربر با create_user
@pytest.mark.django_db
def test_create_user_success(user_data):
    user = User.objects.create_user(
        username=user_data['username'],
        email=user_data['email'],
        password=user_data['password']
    )

    assert user.username == user_data['username']
    assert user.email == user_data['email']
    assert user.check_password(user_data['password'])
    assert user.is_active is True
    assert user.is_superuser is False
    assert user.is_staff is False  # به دلیل @property is_staff
    assert str(user) == user_data['email']


# تست نرمال‌سازی ایمیل در create_user
@pytest.mark.django_db
def test_create_user_email_normalization():
    email = 'TestUser@Example.COM'
    user = User.objects.create_user(
        username='testuser',
        email=email,
        password='Testpass123'
    )

    assert user.email == 'TestUser@example.com'  # نرمال‌سازی به حروف کوچک


# تست خطای ایمیل خالی در create_user
@pytest.mark.django_db
def test_create_user_empty_email():
    with pytest.raises(ValueError) as exc_info:
        User.objects.create_user(
            username='testuser',
            email='',
            password='Testpass123'
        )
    assert str(exc_info.value) == 'user must have email'


# تست خطای نام کاربری خالی در create_user
@pytest.mark.django_db
def test_create_user_empty_username():
    with pytest.raises(ValueError) as exc_info:
        User.objects.create_user(
            username='',
            email='testuser@example.com',
            password='Testpass123'
        )
    assert str(exc_info.value) == 'user must have Username'


# تست ایجاد سوپریوزر با create_superuser
@pytest.mark.django_db
def test_create_superuser_success(user_data):
    user = User.objects.create_superuser(
        username=user_data['username'],
        email=user_data['email'],
        password=user_data['password']
    )

    assert user.username == user_data['username']
    assert user.email == user_data['email']
    assert user.check_password(user_data['password'])
    assert user.is_active is True
    assert user.is_superuser is True
    assert user.is_staff is True  # به دلیل @property is_staff
    assert str(user) == user_data['email']


# تست خطای ایمیل خالی در create_superuser
@pytest.mark.django_db
def test_create_superuser_empty_email():
    with pytest.raises(ValueError) as exc_info:
        User.objects.create_superuser(
            username='testuser',
            email='',
            password='Testpass123'
        )
    assert str(exc_info.value) == 'user must have email'


# تست خطای نام کاربری خالی در create_superuser
@pytest.mark.django_db
def test_create_superuser_empty_username():
    with pytest.raises(ValueError) as exc_info:
        User.objects.create_superuser(
            username='',
            email='testuser@example.com',
            password='Testpass123'
        )
    assert str(exc_info.value) == 'user must have Username'


# تست رفتار is_staff برای کاربر معمولی و سوپریوزر
@pytest.mark.django_db
def test_user_is_staff_property():
    # کاربر معمولی
    user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='Testpass123'
    )
    assert user.is_staff is False

    # سوپریوزر
    superuser = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='Adminpass123'
    )
    assert superuser.is_staff is True