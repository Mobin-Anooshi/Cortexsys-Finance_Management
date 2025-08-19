from django.contrib import admin
from .models import Transaction




@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'title', 'amount', 'type', 'budget', 'date')
    list_filter = ('type', 'budget', 'date')
    search_fields = ('title', 'user__username', 'notes')
    readonly_fields = ('date',)


