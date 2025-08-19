import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from transactions.models import Transaction


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    from accounts.models import User
    user = User.objects.create_user(
        username='test',
        email='test@email.com',
        password='test123456'
    )
    return user

def create_budge():
    from



@pytest.mark.django_db
def test_create_transaction_success(api_client,create_user):
    user = create_user
    api_client.force_authenticate(user=user)
    print(user)
    transaction = {
        'user':user.id,
        'title':'test',
        'amount':100,
        'type':'Income',
        'notes':'test'
    }
    response = api_client.post('/api/transactions/',transaction,format='json')

    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_201_CREATED, f"Error: {response.data}"
