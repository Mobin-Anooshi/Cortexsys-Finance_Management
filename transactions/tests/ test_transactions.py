"""
Test suite for the Transactions app.

This file contains tests for the Transaction model and TransactionAPIView.
The tests cover:
- Creating transactions with valid data (with/without budget, Income/Expense types).
- Validating serializer constraints (e.g., insufficient budget, invalid transaction type).
- Authentication requirements (ensuring unauthenticated requests fail).
- CRUD operations (list, retrieve, partial update, delete).
"""

import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from transactions.models import Transaction
from accounts.models import User
from budgets.models import Budget
from django.utils import timezone


@pytest.fixture
def api_client():
    """Fixture to provide an APIClient instance for making HTTP requests."""
    return APIClient()


@pytest.fixture
def create_user():
    """Fixture to create a test user."""
    user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='ComplexPass123!@#'
    )
    return user


@pytest.fixture
def create_free_budget(create_user):
    """Fixture to create a 'free' budget for a test user."""
    user = create_user
    budget = Budget.objects.create(
        user=user,
        title='free',
        total_amount=999999999999,
        start_date=timezone.now().date()
    )
    return budget


@pytest.fixture
def create_regular_budget(create_user):
    """Fixture to create a regular budget for a test user."""
    user = create_user
    budget = Budget.objects.create(
        user=user,
        title='regular',
        total_amount=1000,
        start_date=timezone.now().date(),
        end_date=timezone.now().date()
    )
    return budget


@pytest.mark.django_db
def test_create_transaction_success_free_budget(api_client, create_user, create_free_budget):
    """
    Test creating a transaction with a 'free' budget successfully.
    Ensures the transaction is created with correct fields and associated with the user and budget.
    """
    user = create_user
    budget = create_free_budget
    api_client.force_authenticate(user=user)
    transaction_data = {
        'title': 'Test Income',
        'amount': 100,
        'type': 'Income',
        'notes': 'Test note',
        'budget': budget.id
    }
    url = reverse('transactions:transaction-list')
    response = api_client.post(url, transaction_data, format='json')
    print(f"Response data: {response.data}")  # Debug output for response
    assert response.status_code == status.HTTP_201_CREATED, f"Error: {response.data}"
    assert Transaction.objects.count() == 1
    transaction = Transaction.objects.first()
    assert transaction.user == user
    assert transaction.title == transaction_data['title']
    assert transaction.amount == transaction_data['amount']
    assert transaction.type == transaction_data['type']
    assert transaction.notes == transaction_data['notes']
    assert transaction.budget == budget


@pytest.mark.django_db
def test_create_transaction_success_no_budget(api_client, create_user):
    """
    Test creating a transaction without a budget successfully.
    Ensures the transaction is created with correct fields and no budget association.
    """
    user = create_user
    api_client.force_authenticate(user=user)
    transaction_data = {
        'title': 'Test Expense',
        'amount': 50,
        'type': 'Expense',
        'notes': 'No budget'
    }
    url = reverse('transactions:transaction-list')
    response = api_client.post(url, transaction_data, format='json')
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_201_CREATED, f"Error: {response.data}"
    assert Transaction.objects.count() == 1
    assert Transaction.objects.first().budget is None


@pytest.mark.django_db
def test_create_transaction_expense_regular_budget(api_client, create_user, create_regular_budget):
    """
    Test creating an Expense transaction with a regular budget.
    Verifies that the budget's total_amount is reduced correctly.
    """
    user = create_user
    budget = create_regular_budget
    api_client.force_authenticate(user=user)
    transaction_data = {
        'title': 'Test Expense',
        'amount': 500,
        'type': 'Expense',
        'notes': 'Test',
        'budget': budget.id
    }
    url = reverse('transactions:transaction-list')
    response = api_client.post(url, transaction_data, format='json')
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_201_CREATED, f"Error: {response.data}"
    budget.refresh_from_db()
    assert budget.total_amount == 500  # 1000 - 500
    assert Transaction.objects.count() == 1


@pytest.mark.django_db
def test_create_transaction_insufficient_budget(api_client, create_user, create_regular_budget):
    """
    Test creating an Expense transaction with insufficient budget funds.
    Ensures the serializer validation rejects the request.
    """
    user = create_user
    budget = create_regular_budget
    api_client.force_authenticate(user=user)
    transaction_data = {
        'title': 'Test Expense',
        'amount': 1500,  # Exceeds budget total_amount=1000
        'type': 'Expense',
        'notes': 'Test',
        'budget': budget.id
    }
    url = reverse('transactions:transaction-list')
    response = api_client.post(url, transaction_data, format='json')
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Error: {response.data}"
    assert 'amount' in response.data
    assert 'You can\'t expense more than this budget' in str(response.data['amount'])


@pytest.mark.django_db
def test_create_transaction_income_regular_budget(api_client, create_user, create_regular_budget):
    """
    Test creating an Income transaction with a non-free budget.
    Ensures the serializer rejects Income transactions for non-free budgets.
    """
    user = create_user
    budget = create_regular_budget
    api_client.force_authenticate(user=user)
    transaction_data = {
        'title': 'Test Income',
        'amount': 100,
        'type': 'Income',
        'notes': 'Test',
        'budget': budget.id
    }
    url = reverse('transactions:transaction-list')
    response = api_client.post(url, transaction_data, format='json')
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Error: {response.data}"
    assert 'type' in response.data
    assert 'You cant Income money to budgets' in str(response.data['type'])


@pytest.mark.django_db
def test_create_transaction_unauthenticated(api_client, create_free_budget):
    """
    Test creating a transaction without authentication.
    Ensures unauthenticated requests are rejected with 401.
    """
    transaction_data = {
        'title': 'Test Income',
        'amount': 100,
        'type': 'Income',
        'notes': 'Test',
        'budget': create_free_budget.id
    }
    url = reverse('transactions:transaction-list')
    response = api_client.post(url, transaction_data, format='json')
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Error: {response.data}"


@pytest.mark.django_db
def test_list_transactions(api_client, create_user, create_free_budget):
    """
    Test listing transactions for an authenticated user.
    Ensures only the user's transactions are returned.
    """
    user = create_user
    budget = create_free_budget
    Transaction.objects.create(user=user, title='Test1', amount=100, type='Income', budget=budget)
    Transaction.objects.create(user=user, title='Test2', amount=200, type='Expense')
    api_client.force_authenticate(user=user)
    url = reverse('transactions:transaction-list')
    response = api_client.get(url)
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_200_OK, f"Error: {response.data}"
    assert len(response.data) == 2
    assert response.data[0]['title'] == 'Test1'
    assert response.data[1]['title'] == 'Test2'


@pytest.mark.django_db
def test_retrieve_transaction(api_client, create_user, create_free_budget):
    """
    Test retrieving a single transaction by ID.
    Ensures the correct transaction details are returned.
    """
    user = create_user
    budget = create_free_budget
    transaction = Transaction.objects.create(user=user, title='Test', amount=100, type='Income', budget=budget)
    api_client.force_authenticate(user=user)
    url = reverse('transactions:transaction-detail', kwargs={'pk': transaction.id})
    response = api_client.get(url)
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_200_OK, f"Error: {response.data}"
    assert response.data['title'] == 'Test'


@pytest.mark.django_db
def test_partial_update_transaction(api_client, create_user, create_free_budget):
    """
    Test partially updating a transaction.
    Ensures the transaction is updated correctly without affecting other fields.
    """
    user = create_user
    budget = create_free_budget
    transaction = Transaction.objects.create(user=user, title='Test', amount=100, type='Income', budget=budget)
    api_client.force_authenticate(user=user)
    update_data = {'notes': 'Updated note'}
    url = reverse('transactions:transaction-detail', kwargs={'pk': transaction.id})
    response = api_client.patch(url, update_data, format='json')
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_200_OK, f"Error: {response.data}"
    transaction.refresh_from_db()
    assert transaction.notes == 'Updated note'
    assert transaction.title == 'Test'  # Ensure other fields are unchanged


@pytest.mark.django_db
def test_destroy_transaction(api_client, create_user, create_free_budget):
    """
    Test deleting a transaction.
    Ensures the transaction is removed and returns 204 status.
    """
    user = create_user
    budget = create_free_budget
    transaction = Transaction.objects.create(user=user, title='Test', amount=100, type='Income', budget=budget)
    api_client.force_authenticate(user=user)
    url = reverse('transactions:transaction-detail', kwargs={'pk': transaction.id})
    response = api_client.delete(url)
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_204_NO_CONTENT, f"Error: {response.data}"
    assert Transaction.objects.count() == 0