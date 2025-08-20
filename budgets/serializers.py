"""
Serializer for the Budget model.

Handles serialization/deserialization of Budget objects for API requests.
Ensures end_date is provided and validates date consistency.
"""

from rest_framework import serializers
from .models import Budget


class BudgetSerializer(serializers.ModelSerializer):
    """
    Serializer for Budget model.
    - Marks 'user' as read-only since it's set from request.user.
    - Ensures end_date is provided and not before start_date.
    """

    class Meta:
        model = Budget
        fields = ('id', 'user', 'title', 'total_amount', 'start_date', 'end_date')
        read_only_fields = ('user',)
        extra_kwargs = {
            'end_date': {'required': True}
        }

    def validate(self, data):
        """
        Validate budget data.
        - Ensure end_date is not before start_date.
        - Ensure total_amount is positive.
        """
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        total_amount = data.get('total_amount')

        if end_date and start_date and end_date < start_date:
            raise serializers.ValidationError({"end_date": "End date cannot be before start date"})
        if total_amount < 0:
            raise serializers.ValidationError({"total_amount": "Total amount must be non-negative"})
        return data