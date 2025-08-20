"""
Test suite for the Budgets app.

This file contains tests for the Budget model and BudgetAPIView.
The tests cover:
- The create_free_budget signal for automatic budget creation on user signup.
- Creating budgets with valid and invalid data (e.g., missing end_date).
- Authentication requirements (ensuring unauthenticated requests fail).
- CRUD operations (list, retrieve, partial update, delete).
"""

import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from budgets.models import Budget
from accounts.models import User
from django.utils import timezone


@pytest.fixture
def api_client():
    """Fixture to provide an APIClient instance for making HTTP requests."""
    return APIClient()


@pytest.fixture
def create_user():
    """Fixture to create a test user, triggering the create_free_budget signal."""
    user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='ComplexPass123!@#'
    )
    return user


@pytest.mark.django_db
def test_create_free_budget_signal(create_user):
    """
    Test the create_free_budget signal.
    Ensures a 'free' budget is created automatically when a user is created.
    """
    user = create_user
    budget = Budget.objects.get(user=user, title='free')
    assert budget is not None, "Free budget was not created"
    assert budget.total_amount == 999999999999, "Incorrect total_amount for free budget"
    assert budget.start_date == timezone.now().date(), "Incorrect start_date"
    assert budget.end_date is None, "Free budget should have no end_date"


@pytest.mark.django_db
def test_create_budget_success(api_client, create_user):
    """
    Test creating a budget successfully.
    Ensures the budget is created with correct fields and associated with the user.
    """
    user = create_user
    api_client.force_authenticate(user=user)
    budget_data = {
        'title': 'Test Budget',
        'total_amount': 1000,
        'start_date': timezone.now().date(),
        'end_date': timezone.now().date()
    }
    url = reverse('budgets:budget-list')
    response = api_client.post(url, budget_data, format='json')
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_201_CREATED, f"Error: {response.data}"
    assert Budget.objects.count() == 2, "Expected two budgets (free + new)"  # Includes free budget
    budget = Budget.objects.get(title='Test Budget')
    assert budget.user == user
    assert budget.total_amount == budget_data['total_amount']


@pytest.mark.django_db
def test_create_budget_missing_end_date(api_client, create_user):
    """
    Test creating a budget with missing end_date.
    Ensures the serializer rejects the request due to required end_date.
    """
    user = create_user
    api_client.force_authenticate(user=user)
    budget_data = {
        'title': 'Test Budget',
        'total_amount': 1000,
        'start_date': timezone.now().date()
    }
    url = reverse('budgets:budget-list')
    response = api_client.post(url, budget_data, format='json')
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Error: {response.data}"
    assert 'end_date' in response.data, "Expected error for missing end_date"


@pytest.mark.django_db
def test_create_budget_unauthenticated(api_client):
    """
    Test creating a budget without authentication.
    Ensures unauthenticated requests are rejected with 401.
    """
    budget_data = {
        'title': 'Test Budget',
        'total_amount': 1000,
        'start_date': timezone.now().date(),
        'end_date': timezone.now().date()
    }
    url = reverse('budgets:budget-list')
    response = api_client.post(url, budget_data, format='json')
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Error: {response.data}"


@pytest.mark.django_db
def test_list_budgets(api_client, create_user):
    """
    Test listing budgets for an authenticated user.
    Ensures only the user's budgets are returned, including the free budget.
    """
    user = create_user
    Budget.objects.create(
        user=user,
        title='Test1',
        total_amount=1000,
        start_date=timezone.now().date(),
        end_date=timezone.now().date()
    )
    api_client.force_authenticate(user=user)
    url = reverse('budgets:budget-list')
    response = api_client.get(url)
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_200_OK, f"Error: {response.data}"
    assert len(response.data) == 2, "Expected two budgets (free + Test1)"
    assert response.data[1]['title'] == 'Test1'


@pytest.mark.django_db
def test_retrieve_budget(api_client, create_user):
    """
    Test retrieving a single budget by ID.
    Ensures the correct budget details are returned.
    """
    user = create_user
    budget = Budget.objects.create(
        user=user,
        title='Test',
        total_amount=1000,
        start_date=timezone.now().date(),
        end_date=timezone.now().date()
    )
    api_client.force_authenticate(user=user)
    url = reverse('budgets:budget-detail', kwargs={'pk': budget.id})
    response = api_client.get(url)
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_200_OK, f"Error: {response.data}"
    assert response.data['title'] == 'Test'


@pytest.mark.django_db
def test_partial_update_budget(api_client, create_user):
    """
    Test partially updating a budget.
    Ensures the budget is updated correctly without affecting other fields.
    """
    user = create_user
    budget = Budget.objects.create(
        user=user,
        title='Test',
        total_amount=1000,
        start_date=timezone.now().date(),
        end_date=timezone.now().date()
    )
    api_client.force_authenticate(user=user)
    update_data = {'total_amount': 2000}
    url = reverse('budgets:budget-detail', kwargs={'pk': budget.id})
    response = api_client.patch(url, update_data, format='json')
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_200_OK, f"Error: {response.data}"
    budget.refresh_from_db()
    assert budget.total_amount == 2000, "Budget total_amount was not updated"
    assert budget.title == 'Test', "Budget title should remain unchanged"


@pytest.mark.django_db
def test_destroy_budget(api_client, create_user):
    """
    Test deleting a budget.
    Ensures the budget is removed and the free budget remains.
    """
    user = create_user
    budget = Budget.objects.create(
        user=user,
        title='Test',
        total_amount=1000,
        start_date=timezone.now().date(),
        end_date=timezone.now().date()
    )
    api_client.force_authenticate(user=user)
    url = reverse('budgets:budget-detail', kwargs={'pk': budget.id})
    response = api_client.delete(url)
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_204_NO_CONTENT, f"Error: {response.data}"
    assert Budget.objects.filter(title='Test').count() == 0, "Budget was not deleted"
    assert Budget.objects.filter(title='free').count() == 1, "Free budget should remain"