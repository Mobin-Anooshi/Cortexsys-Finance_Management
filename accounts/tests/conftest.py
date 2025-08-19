import pytest
from django.test import TestCase

@pytest.fixture(autouse=True)
def setup_django(django_test_environment):
    pass