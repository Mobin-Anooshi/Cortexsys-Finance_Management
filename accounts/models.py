from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManagers
# Create your models here.


class User(AbstractBaseUser):
    username = models.CharField(max_length=100,unique=True)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ('email',)

    objects = UserManagers()

    def __str__(self) -> str:
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_superuser
