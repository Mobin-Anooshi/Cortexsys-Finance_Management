"""
Views for the Budgets app.

Implements RESTful API endpoints for Budget CRUD operations using ViewSet.
Requires authentication for all actions, ensuring users can only access their own budgets.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from .models import Budget
from .serializers import BudgetSerializer


class BudgetAPIView(viewsets.ViewSet):
    """
    API ViewSet for Budget model.
    Handles listing, creating, retrieving, updating, and deleting budgets.
    All actions require JWT authentication and are restricted to the authenticated user's data.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer

    def list(self, request):
        """
        List all budgets for the authenticated user.
        Returns serialized budget data.
        """
        budgets = self.queryset.filter(user=request.user)
        serializer = self.serializer_class(budgets, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request):
        """
        Create a new budget for the authenticated user.
        Sets the user field from request.user and validates data.
        """
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        """
        Retrieve a specific budget by ID.
        Ensures the budget belongs to the authenticated user.
        """
        budget = get_object_or_404(self.queryset, pk=pk, user=request.user)
        serializer = self.serializer_class(budget)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, pk=None):
        """
        Partially update a budget by ID.
        Ensures the budget belongs to the authenticated user.
        """
        budget = get_object_or_404(self.queryset, pk=pk, user=request.user)
        serializer = self.serializer_class(budget, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Delete a budget by ID.
        Ensures the budget belongs to the authenticated user.
        """
        budget = get_object_or_404(self.queryset, pk=pk, user=request.user)
        budget.delete()
        return Response({"message": "Budget deleted"}, status=status.HTTP_204_NO_CONTENT)