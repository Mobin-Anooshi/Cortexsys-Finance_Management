"""
Signals for the Budgets app.

Automatically creates a 'free' budget when a user is created or ensures it exists for existing users.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now
from accounts.models import User
from .models import Budget


@receiver(post_save, sender=User)
def create_free_budget(sender, instance, created, **kwargs):
    """
    Signal handler to create or ensure a 'free' budget for a user.
    - Creates a free budget on user creation.
    - Ensures a free budget exists for existing users without one.
    """
    if created:
        Budget.objects.get_or_create(
            user=instance,
            title="free",
            defaults={
                "total_amount": 999999999999,
                "start_date": now().date(),
                "end_date": None
            }
        )
    else:
        if not Budget.objects.filter(user=instance, title="free").exists():
            Budget.objects.create(
                user=instance,
                title="free",
                total_amount=999999999999,
                start_date=now().date(),
                end_date=None
            )