from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import ugettext_lazy as _

# Choices type
TRANSACTION_TYPE = [
    (0, 'Deposit'),  # Nap tien
    (1, 'Withdrawal'),  # Rut tien
    (2, 'Commission'),  # Tien hoa hong
]
TRANSACTION_STATUS = [
    (0, 'Pending'),  # Cho duyet
    (1, 'Completed'),  # Da duyet
]


class MyUserManager(BaseUserManager):
    def create_user(self, username, fullname, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not username:
            raise ValueError('Users must have an username')

        user = self.model(
            username=username,
            fullname=fullname
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, fullname, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            username,
            fullname=fullname,
            password=password,
        )
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    email = models.EmailField(null=True)
    username = models.CharField(unique=True, max_length=255, default="", null=False)
    fullname = models.CharField(max_length=255, default="", null=False)
    phone = models.CharField(max_length=20, default="", null=False)
    balance = models.IntegerField(default=0, null=False)
    is_superuser = models.BooleanField(default=False, null=False)
    is_admin = models.BooleanField(default=False, null=False)
    is_lead = models.BooleanField(default=False, null=False)
    is_active = models.BooleanField(default=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['fullname']

    object = MyUserManager()

    def __str__(self):
        return self.fullname

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser


class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user', db_column='user')
    type = models.IntegerField(choices=TRANSACTION_TYPE, blank=False, null=False, db_column='type')
    amount = models.FloatField(blank=False, null=False, db_column='amount')
    status = models.IntegerField(choices=TRANSACTION_STATUS, blank=False, null=False, db_column='status')
    extra_info = models.TextField(max_length=3000, blank=True, null=True, db_column='extra_info')
    created = models.DateTimeField(auto_now_add=True, db_column='created')

    class Meta:
        managed = True
        db_table = 'transaction'


class ServerInfo(models.Model):
    ip = models.CharField(max_length=255, blank=False, null=False, default='ip')
    user_name = models.CharField(max_length=255, blank=False, null=False, default='user_name')
    pwd = models.CharField(max_length=255, blank=False, null=False, default='pwd')
    created = models.DateTimeField(auto_now_add=True, db_column='created')

    class Meta:
        managed = True
        db_table = 'server_info'


class AccountMT4(models.Model):
    id = models.IntegerField(primary_key=True, db_column='id')
    pwd = models.CharField(max_length=255, blank=False, null=False, db_column='pwd')
    name = models.TextField(max_length=255, blank=False, null=False, db_column='name')
    is_parent = models.BooleanField(blank=False, null=False, default=False, db_column='is_parent')
    server = models.ForeignKey(ServerInfo, on_delete=models.DO_NOTHING, blank=True, null=True, db_column='server')
    created = models.DateTimeField(auto_now_add=True, db_column='created')

    class Meta:
        managed = True
        db_table = 'account_mt4'
