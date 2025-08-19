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

    def clean(self):
        if self.budget.title != "free":
            if self.budget.start_date > self.date.date() or (
                self.budget.end_date and self.budget.end_date < self.date.date()
            ):
                raise ValidationError("You cant transaction in this time")

            transactions = Transaction.objects.filter(budget=self.budget).exclude(pk=self.pk)
            total = 0

            for t in transactions:
                if t.type == "Expense":
                    total += t.amount
                elif t.type == "Income":
                    total -= t.amount

            if self.type == "Expense":
                total += self.amount
            elif self.type == "Income":
                total -= self.amount

            if total > self.budget.total_amount:
                raise ValidationError("you cant income in this budgets")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
