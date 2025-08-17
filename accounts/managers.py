from django.contrib.auth.models import BaseUserManager


class UserManagers(BaseUserManager):

    def create_user(self,username, email, password):
        if not email:
            raise ValueError('user must have email')
        if not username:
            raise ValueError('user must have Username')

        user = self.model(username=username,email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(username=username ,email=email, password=password)
        user.is_superuser = True
        user.save(using=self._db)
        return user
