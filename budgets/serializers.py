from rest_framework import serializers
from .models import Budget




class BudgetSerializers(serializers.ModelSerializer):
    class Meta:
        model = Budget
        fields = '__all__'
        extra_kwargs = {
            'end_time':{'required':True}
        }
        read_only_fields = ('user',)