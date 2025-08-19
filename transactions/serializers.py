from rest_framework import serializers
from .models import Transaction


class TransactionSerializers(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('user','title','amount','type','notes')
        read_only_fields = ('user',)





