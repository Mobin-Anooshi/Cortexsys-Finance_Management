from rest_framework import serializers
from .models import Transaction
from budgets.models import Budget
from django.db import transaction


class TransactionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('user','title','amount','type','notes','budget')
        read_only_fields = ('user',)


    def validate(self, data):
        budget = data.get('budget')
        amount = data.get('amount')
        type_ = data.get('type')

        if budget and budget.title != "free":
            budget_ = Budget.objects.filter(pk=budget.id).first()
            if type_ == "Expense":
                if budget_.total_amount >= amount:
                    with transaction.atomic():
                        budget_.total_amount -= amount
                        budget_.save()
                else:
                    raise serializers.ValidationError({"amount": f"You can't expense more than this budget, \n your budgets: {budget_.total_amount}"})
            else:
                raise serializers.ValidationError({'type':'You cant Income money to budgets'})
        return data






