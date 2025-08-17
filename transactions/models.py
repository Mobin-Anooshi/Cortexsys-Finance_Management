from django.db import models
from accounts.models import User
# Create your models here.


class Transaction(models.Model):

    TYPE_CHOICES = [
        ('Income','income'),
        ('Expense','expense')
    ]

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    amount = models.PositiveBigIntegerField()
    type = models.CharField(max_length=8,choices=TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True,null=True)

    def __str__(self):
        return f'{self.user}-{self.amount}-{self.type}'