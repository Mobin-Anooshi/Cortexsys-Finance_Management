import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status




@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user_data():
    return {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'Testpass123'
    }


@pytest.mark.django_db
def test_create_user_success(user_data):
    from accounts.models import User
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
    assert user.is_staff is False
    assert str(user) == user_data['email']



@pytest.mark.django_db
def test_create_user_empty_email():
    from accounts.models import User
    with pytest.raises(ValueError) as exc_info:
        User.objects.create_user(
            username='testuser',
            email='',
            password='Testpass123'
        )
    assert str(exc_info.value) == 'user must have email'



@pytest.mark.django_db
def test_user_register_success(api_client, user_data):
    from accounts.models import User
    url = reverse('accounts:register')  # استفاده از reverse به جای مسیر دستی
    response = api_client.post(url, user_data, format='json')

    assert response.status_code == status.HTTP_201_CREATED, f"Error: {response.data}"
    assert User.objects.count() == 1
    assert User.objects.first().username == user_data['username']
    assert 'password' not in response.data

@pytest.mark.django_db
def test_user_username_admin(api_client):
    from accounts.models import User
    url = reverse('accounts:register')
    data = {'username':'admin','email':'admin@email.com','password':'admin12345678'}
    response = api_client.post(url,data,format='json')

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert User.objects.count() == 0
    assert response.data['username'][0] == 'username cant be admin'
