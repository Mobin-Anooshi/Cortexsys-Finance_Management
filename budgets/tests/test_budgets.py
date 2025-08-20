import pytest
from rest_framework.test import APIClient
from django.urls import reverse
from rest_framework import status
from budgets.models import Budget
from accounts.models import User
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

# تست سیگنال create_free_budget هنگام ایجاد کاربر
@pytest.mark.django_db
def test_create_free_budget_signal(create_user):
    user = create_user
    budget = Budget.objects.get(user=user, title='free')
    assert budget is not None
    assert budget.total_amount == 999999999999
    assert budget.start_date == timezone.now().date()
    assert budget.end_date is None

# تست ایجاد بودجه موفق
@pytest.mark.django_db
def test_create_budget_success(api_client, create_user):
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
    assert Budget.objects.count() == 2  # شامل بودجه free
    budget = Budget.objects.get(title='Test Budget')
    assert budget.user == user
    assert budget.total_amount == 1000

# تست خطا برای end_date گم‌شده
@pytest.mark.django_db
def test_create_budget_missing_end_date(api_client, create_user):
    user = create_user
    api_client.force_authenticate(user=user)
    budget_data = {
        'title': 'Test Budget',
        'total_amount': 1000,
        'start_date': timezone.now().date()
    }
    url = reverse('budgets:budget-list')
    response = api_client.post(url, budget_data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'end_date' in response.data

# تست ایجاد بودجه بدون احراز هویت
@pytest.mark.django_db
def test_create_budget_unauthenticated(api_client):
    budget_data = {
        'title': 'Test Budget',
        'total_amount': 1000,
        'start_date': timezone.now().date(),
        'end_date': timezone.now().date()
    }
    url = reverse('budgets:budget-list')
    response = api_client.post(url, budget_data, format='json')
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

# تست لیست بودجه‌ها
@pytest.mark.django_db
def test_list_budgets(api_client, create_user):
    user = create_user
    Budget.objects.create(user=user, title='Test1', total_amount=1000, start_date=timezone.now().date(), end_date=timezone.now().date())
    api_client.force_authenticate(user=user)
    url = reverse('budgets:budget-list')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 2  # شامل بودجه free
    assert response.data[1]['title'] == 'Test1'

# تست retrieve بودجه
@pytest.mark.django_db
def test_retrieve_budget(api_client, create_user):
    user = create_user
    budget = Budget.objects.create(user=user, title='Test', total_amount=1000, start_date=timezone.now().date(), end_date=timezone.now().date())
    api_client.force_authenticate(user=user)
    url = reverse('budgets:budget-detail', kwargs={'pk': budget.id})
    response = api_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'Test'

# تست به‌روزرسانی جزئی بودجه
@pytest.mark.django_db
def test_partial_update_budget(api_client, create_user):
    user = create_user
    budget = Budget.objects.create(user=user, title='Test', total_amount=1000, start_date=timezone.now().date(), end_date=timezone.now().date())
    api_client.force_authenticate(user=user)
    update_data = {'total_amount': 2000}
    url = reverse('budgets:budget-detail', kwargs={'pk': budget.id})
    response = api_client.patch(url, update_data, format='json')
    assert response.status_code == status.HTTP_200_OK
    budget.refresh_from_db()
    assert budget.total_amount == 2000

# تست حذف بودجه
@pytest.mark.django_db
def test_destroy_budget(api_client, create_user):
    user = create_user
    budget = Budget.objects.create(user=user, title='Test', total_amount=1000, start_date=timezone.now().date(), end_date=timezone.now().date())
    api_client.force_authenticate(user=user)
    url = reverse('budgets:budget-detail', kwargs={'pk': budget.id})
    response = api_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Budget.objects.filter(title='Test').count() == 0
    assert Budget.objects.filter(title='free').count() == 1  # بودجه free باقی می‌مونه