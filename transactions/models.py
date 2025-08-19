from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import User
from budgets.models import Budget
from django.utils import timezone



class Transaction(models.Model):

    TYPE_CHOICES = [
        ('Income', 'income'),
        ('Expense', 'expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    amount = models.PositiveBigIntegerField()
    type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    date = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    budget = models.ForeignKey(Budget, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.user} - {self.amount} - {self.type}'
