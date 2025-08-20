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
    return APIClient()

@pytest.fixture
def create_user():
    user = User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='ComplexPass123!@#'
    )
    return user

@pytest.fixture
def create_free_budget(create_user):
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
    user = create_user
    budget = Budget.objects.create(
        user=user,
        title='regular',
        total_amount=1000,
        start_date=timezone.now().date(),
        end_date=timezone.now().date()
    )
    return budget

# تست ایجاد تراکنش موفق (با بودجه free)
@pytest.mark.django_db
def test_create_transaction_success_free_budget(api_client, create_user, create_free_budget):
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
    print(f"Response data: {response.data}")
    assert response.status_code == status.HTTP_201_CREATED, f"Error: {response.data}"
    assert Transaction.objects.count() == 1
    transaction = Transaction.objects.first()
    assert transaction.user == user
    assert transaction.title == transaction_data['title']
    assert transaction.amount == transaction_data['amount']
    assert transaction.type == transaction_data['type']
    assert transaction.notes == transaction_data['notes']
    assert transaction.budget == budget

# تست ایجاد تراکنش موفق (بدون بودجه)
@pytest.mark.django_db
def test_create_transaction_success_no_budget(api_client, create_user):
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
    assert response.status_code == status.HTTP_201_CREATED
    assert Transaction.objects.count() == 1
    assert Transaction.objects.first().budget is None

# تست ایجاد تراکنش با بودجه غیر free و نوع Expense (موفق)
@pytest.mark.django_db
def test_create_transaction_expense_regular_budget(api_client, create_user, create_regular_budget):
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
    assert response.status_code == status.HTTP_201_CREATED
    budget.refresh_from_db()
    assert budget.total_amount == 500  # 1000 - 500
    assert Transaction.objects.count() == 1

# تست خطا برای تراکنش Expense با بودجه ناکافی
@pytest.mark.django_db
def test_create_transaction_insufficient_budget(api_client, create_user, create_regular_budget):
    user = create_user
    budget = create_regular_budget
    api_client.force_authenticate(user=user)
    transaction_data = {
        'title': 'Test Expense',
        'amount': 1500,  # بیشتر از total_amount=1000
        'type': 'Expense',
        'notes': 'Test',
        'budget': budget.id
    }
    url = reverse('transactions:transaction-list')
    response = api_client.post(url, transaction_data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'amount' in response.data
    assert 'You can\'t expense more than this budget' in str(response.data['amount'])

# تست خطا برای تراکنش Income با بودجه غیر free
@pytest.mark.django_db
def test_create_transaction_income_regular_budget(api_client, create_user, create_regular_budget):
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
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'type' in response.data
    assert 'You cant Income money to budgets' in str(response.data['type'])

# تست ایجاد تراکنش بدون احراز هویت
@pytest.mark.django_db
def test_create_transaction_unauthenticated(api_client, create_free_budget):
    transaction_data = {
        'title': 'Test Income',
        'amount': 100,
        'type': 'Income',
        'notes': 'Test',
        'budget': create_free_budget.id
    }
    url = reverse('transactions:transaction-list')
    response = api_client.post(url, transaction_data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# تست لیست تراکنش‌ها
@pytest.mark.django_db
def test_list_transactions(api_client, create_user, create_free_budget):
    user = create_user
    budget = create_free_budget
    Transaction.objects.create(user=user, title='Test1', amount=100, type='Income', budget=budget)
    Transaction.objects.create(user=user, title='Test2', amount=200, type='Expense')
    api_client.force_authenticate(user=user)
    url = reverse('transactions:transaction-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2
    assert response.data[0]['title'] == 'Test1'
    assert response.data[1]['title'] == 'Test2'

# تست retrieve تراکنش
@pytest.mark.django_db
def test_retrieve_transaction(api_client, create_user, create_free_budget):
    user = create_user
    budget = create_free_budget
    transaction = Transaction.objects.create(user=user, title='Test', amount=100, type='Income', budget=budget)
    api_client.force_authenticate(user=user)
    url = reverse('transactions:transaction-detail', kwargs={'pk': transaction.id})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'Test'

# تست به‌روزرسانی جزئی تراکنش
@pytest.mark.django_db
def test_partial_update_transaction(api_client, create_user, create_free_budget):
    user = create_user
    budget = create_free_budget
    transaction = Transaction.objects.create(user=user, title='Test', amount=100, type='Income', budget=budget)
    api_client.force_authenticate(user=user)
    update_data = {'notes': 'Updated note'}
    url = reverse('transactions:transaction-detail', kwargs={'pk': transaction.id})
    response = api_client.patch(url, update_data, format='json')
    assert response.status_code == status.HTTP_200_OK
    transaction.refresh_from_db()
    assert transaction.notes == 'Updated note'

# تست حذف تراکنش
@pytest.mark.django_db
def test_destroy_transaction(api_client, create_user, create_free_budget):
    user = create_user
    budget = create_free_budget
    transaction = Transaction.objects.create(user=user, title='Test', amount=100, type='Income', budget=budget)
    api_client.force_authenticate(user=user)
    url = reverse('transactions:transaction-detail', kwargs={'pk': transaction.id})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Transaction.objects.count() == 0