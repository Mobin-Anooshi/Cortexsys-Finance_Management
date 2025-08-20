"""
Views for the Transactions app.

Implements RESTful API endpoints for Transaction CRUD operations using ViewSet.
Requires authentication for all actions, ensuring users can only access their own transactions.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from .models import Transaction
from .serializers import TransactionSerializer


class TransactionAPIView(viewsets.ViewSet):
    """
    API ViewSet for Transaction model.
    Handles listing, creating, retrieving, updating, and deleting transactions.
    All actions require JWT authentication and are restricted to the authenticated user's data.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

    def list(self, request):
        """
        List all transactions for the authenticated user.
        Returns serialized transaction data.
        """
        transactions = self.queryset.filter(user=request.user)
        serializer = self.serializer_class(transactions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """
        Create a new transaction for the authenticated user.
        Sets the user field from request.user and validates data.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific transaction by ID.
        Ensures the transaction belongs to the authenticated user.
        """
        transaction = get_object_or_404(self.queryset, pk=pk, user=request.user)
        serializer = self.serializer_class(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        """
        Partially update a transaction by ID.
        Ensures the transaction belongs to the authenticated user.
        """
        transaction = get_object_or_404(self.queryset, pk=pk, user=request.user)
        serializer = self.serializer_class(transaction, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a transaction by ID.
        Ensures the transaction belongs to the authenticated user.
        """
        transaction = get_object_or_404(self.queryset, pk=pk, user=request.user)
        transaction.delete()
        return Response({"message": "Transaction deleted"}, status=status.HTTP_204_NO_CONTENT)