from django.db import models
from accounts.models import User
# Create your models here.



class Budget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    total_amount = models.PositiveBigIntegerField()
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)  # ← تغییر مهم

    def __str__(self):
        if self.end_date:
            days = (self.end_date - self.start_date).days
            return f'{self.title} - {self.total_amount} - {days} days'
        return f'{self.title} - {self.total_amount} - no end date'
