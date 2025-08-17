from rest_framework import serializers
from .models import Transaction


class TransactionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('user','title','amount','type','notes')
        read_only_fields = ('user',)


        # def validate(self,data):
        #     if data['amount'] == 'expense':
        #         amounts = Transaction.objects.filter(user=data['user'])
        #         count = 0
        #         for amount in amounts:
        #             if amount.type == 'expense':
        #                 count -= amount.amount





