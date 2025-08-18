from django.db import models
from accounts.models import User
# Create your models here.



class Budget(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    total_amount = models.PositiveBigIntegerField()
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f'{self.title} - {self.total_amount} - {str(self.end_date-self.start_date)} days'



