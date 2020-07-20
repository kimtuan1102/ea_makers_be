from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _


# User Auth Model


class MyUserManager(BaseUserManager):
    """
    A custom user manager to deal with emails as unique identifiers for auth
    instead of usernames. The default that's used is "UserManager"
    """

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, null=True)
    name = models.CharField(max_length=1024, default="", null=False)
    phone = models.CharField(max_length=20, default="", null=False)
    created_time = models.DateTimeField(blank=True)
    last_activity = models.DateTimeField(blank=True, null=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    USERNAME_FIELD = 'email'

    @staticmethod
    def main_key_field():
        return "id"

    @staticmethod
    def sub_key_field():
        return None

    objects = MyUserManager()

    class Meta:
        managed = False
        db_table = 'user'

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email


# App Model
class AccountMT4(models.Model):
    id = models.IntegerField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=False, default='', db_column='name')
    is_parent = models.BooleanField(default=False, db_column='is_parent')
    description = models.CharField(max_length=255, blank=True, db_column='description')
    created = models.DateTimeField(auto_now_add=True, db_column='created')
    updated = models.DateTimeField(auto_now=True, db_column='updated')

    class Meta:
        db_table = 'account_mt4'


class Expert(models.Model):
    name = models.CharField(max_length=255, blank=False, db_column='name')
    description = models.CharField(max_length=255, blank=True, db_column='description')
    created = models.DateTimeField(auto_now_add=True, db_column='created')
    updated = models.DateTimeField(auto_now=True, db_column='updated')

    class Meta:
        db_table = 'experts'


class ExpertConfig(models.Model):
    expert = models.ForeignKey(Expert, related_name='expert', on_delete=models.CASCADE, db_column='expert')
    config_key = models.CharField(max_length=255, db_column='config_key')
    config_value = models.CharField(max_length=255, db_column='config_value')
    created = models.DateTimeField(auto_now_add=True, db_column='created')
    updated = models.DateTimeField(auto_now=True, db_column='updated')

    class Meta:
        db_table = 'experts_config'


class ExpertLogs(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', db_column='user')
    account_mt4 = models.ForeignKey(AccountMT4, on_delete=models.CASCADE, related_name='account_mt4')
    license = models.CharField(max_length=255, blank=False, db_column='license')
    expert = models.ForeignKey(Expert, on_delete=models.CASCADE, related_name='expert')
    volume = models.FloatField(blank=False, db_column='volume')
    created = models.DateTimeField(auto_now_add=True, db_column='created')

    class Meta:
        db_table = 'experts_log'
