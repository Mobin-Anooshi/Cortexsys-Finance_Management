"""
Serializer for the Transaction model.

Handles serialization/deserialization of Transaction objects for API requests.
Includes validations for budget constraints and transaction types.
"""

from rest_framework import serializers
from .models import Transaction
from budgets.models import Budget
from django.db import transaction as db_transaction


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer for Transaction model.
    - Marks 'user' as read-only since it's set from request.user.
    - Validates budget-related rules (e.g., sufficient funds for Expense, no Income for non-free budgets).
    """

    class Meta:
        model = Transaction
        fields = ('id', 'user', 'title', 'amount', 'type', 'notes', 'budget', 'date')
        read_only_fields = ('user', 'date')

    def validate(self, data):
        """
        Validate transaction data.
        - For Expense transactions with a non-free budget, ensure budget has sufficient funds.
        - Prevent Income transactions for non-free budgets.
        """
        budget = data.get('budget')
        amount = data.get('amount')
        type_ = data.get('type')

        if budget and budget.title != "free":
            budget_ = Budget.objects.filter(pk=budget.id).first()
            if not budget_:
                raise serializers.ValidationError({"budget": "Invalid budget ID"})
            if type_ == "Expense":
                if budget_.total_amount < amount:
                    raise serializers.ValidationError({
                        "amount": f"You can't expense more than this budget, available: {budget_.total_amount}"
                    })
                # Update budget total_amount within a transaction
                with db_transaction.atomic():
                    budget_.total_amount -= amount
                    budget_.save()
            else:
                raise serializers.ValidationError({"type": "You cannot add Income to non-free budgets"})
        return data

    def validate_amount(self, value):
        """Ensure amount is positive."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive")
        return value

    def validate_type(self, value):
        """Ensure type is valid."""
        valid_types = [choice[0] for choice in Transaction.TYPE_CHOICES]
        if value not in valid_types:
            raise serializers.ValidationError(f"Type must be one of {valid_types}")
        return value