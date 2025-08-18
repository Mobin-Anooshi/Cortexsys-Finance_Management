from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Budget
from .serializers import BudgetSerializers
from rest_framework_simplejwt.authentication import JWTAuthentication


class BudgetAPIView(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Budget.objects.all()

    def list(self, request):
        data = self.queryset.filter(user=request.user)
        ser_data = BudgetSerializers(instance=data, many=True)
        return Response(ser_data.data)

    def create(self, request):
        ser_data = BudgetSerializers(data=request.data)
        if ser_data.is_valid(raise_exception=True):
            ser_data.save(user=request.user)
            return Response(ser_data.data, status=status.HTTP_201_CREATED)
        return Response(ser_data.errors)

    def partial_update(self, request, pk=None):
        data = get_object_or_404(Budget, pk=pk, user=request.user)
        ser_data = BudgetSerializers(instance=data, data=request.data, partial=True)
        if ser_data.is_valid(raise_exception=True):
            ser_data.save()
            return Response(ser_data.data)
        return Response(ser_data.errors)

    def retrieve(self, request, pk=None):
        data = get_object_or_404(Budget, pk=pk, user=request.user)
        ser_data = BudgetSerializers(instance=data)
        return Response(ser_data.data)

    def destroy(self, request, pk=None):
        data = get_object_or_404(Budget, pk=pk, user=request.user)
        data.delete()
        return Response({'message': 'Deleted'}, status=status.HTTP_204_NO_CONTENT)
