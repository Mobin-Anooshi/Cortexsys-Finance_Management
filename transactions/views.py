from django.shortcuts import render,get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from .serializers import TransactionSerializers
from .models import Transaction
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
# Create your views here.


class TransactionAPIView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Transaction.objects.all()

    def list(self, request):
        data = self.queryset.filter(user=request.user)
        ser_data = TransactionSerializers(instance=data ,many=True)
        return  Response(ser_data.data)

    def create(self, request):
        ser_data = TransactionSerializers(data=request.data)
        if ser_data.is_valid(raise_exception=True):
            ser_data.save(user=request.user)
            return Response(ser_data.data, status=status.HTTP_201_CREATED)
        return Response(ser_data.errors)

    def partial_update(self, request, pk=None):
        data = get_object_or_404(Transaction, pk=pk, user=request.user)
        ser_data = TransactionSerializers(instance=data, data=request.data, partial=True)
        if ser_data.is_valid(raise_exception=True):
            ser_data.save()
            return Response(ser_data.data)
        return Response(ser_data.errors)

    def retrieve(self, request, pk=None):
        data = get_object_or_404(Transaction, pk=pk, user=request.user)
        ser_data = TransactionSerializers(instance=data)
        return Response(ser_data.data)

    def destroy(self, request, pk=None):
        data = get_object_or_404(Transaction, pk=pk, user=request.user)
        data.delete()
        return Response({'message': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)

