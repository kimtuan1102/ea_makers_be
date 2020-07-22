from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager

# Choices type
TRANSACTION_TYPE = [
    (0, 'Deposit'),  # Nap tien
    (1, 'Withdrawal'),  # Rut tien
    (2, 'Commission'),  # Tien hoa hong
    (3, 'OrderPackage'),  # Mua goi
]
TRANSACTION_STATUS = [
    (0, 'Pending'),  # Cho duyet
    (1, 'Completed'),  # Da duyet
    (2, 'Canceled'),  # Huy
]
ACCOUNT_HISTORY_STATUS = [
    (0, 'Win'),
    (1, 'Loss'),
    (2, 'Draw'),
]
ORDER_TYPE = [
    (0, 'SelfOrder'),
    (1, 'EACopy'),
]
ACCOUNT_CONFIG_STATUS = [
    (0, 'Wait for creation'),
    (1, 'Creating'),
    (2, 'Running'),
    (3, 'Paused'),
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


class User(AbstractBaseUser, PermissionsMixin):
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

    objects = MyUserManager()

    class Meta:
        managed = True
        db_table = 'user'

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
    ip = models.CharField(max_length=255, blank=False, null=False, db_column='ip')
    user_name = models.CharField(max_length=255, blank=False, null=False, db_column='user_name')
    pwd = models.CharField(max_length=255, blank=False, null=False, db_column='pwd')
    created = models.DateTimeField(auto_now_add=True, db_column='created')

    class Meta:
        managed = True
        db_table = 'server_info'


class Office(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, db_column='name')
    created = models.DateTimeField(auto_now_add=True, db_column='created')
    updated = models.DateTimeField(auto_now=True, db_column='updated')

    class Meta:
        managed = True
        db_table = 'office'


class AccountMT4(models.Model):
    id = models.IntegerField(primary_key=True, db_column='id')
    pwd = models.CharField(max_length=255, blank=False, null=False, db_column='pwd')
    name = models.TextField(max_length=255, blank=False, null=False, db_column='name')
    office = models.ForeignKey(Office, related_name='office', on_delete=models.CASCADE, blank=False, null=False,
                               db_column='office')
    is_parent = models.BooleanField(blank=False, null=False, default=False, db_column='is_parent')
    server = models.ForeignKey(ServerInfo, related_name='server', on_delete=models.DO_NOTHING, blank=True, null=True,
                               db_column='server')
    created = models.DateTimeField(auto_now_add=True, db_column='created')

    class Meta:
        managed = True
        db_table = 'account_mt4'


class AccountHistory(models.Model):
    account = models.ForeignKey(AccountMT4, on_delete=models.CASCADE, db_column='account')
    amount = models.FloatField(blank=False, null=False, db_column='amount')
    symbol = models.CharField(max_length=255, blank=False, null=False, db_column='symbol')
    type = models.IntegerField(choices=ORDER_TYPE, db_column='type', blank=False, null=False)
    status = models.IntegerField(choices=ACCOUNT_HISTORY_STATUS, db_column='status', blank=False, null=False)
    open_time = models.DateTimeField(db_column='open_time')
    close_time = models.DateTimeField(db_column='close_time')

    class Meta:
        managed = True
        db_table = 'account_history'


class Package(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, db_column='name')
    price = models.FloatField(db_column='price', blank=False, null=False)
    commission = models.FloatField(db_column='commission', blank=False, null=False)

    class Meta:
        managed = True
        db_table = 'package'


class AccountConfig(models.Model):
    account = models.ForeignKey(AccountMT4, on_delete=models.CASCADE, related_name='account', db_column='account')
    parent = models.ForeignKey(AccountMT4, on_delete=models.CASCADE, related_name='parent', db_column='parent')
    status = models.IntegerField(choices=ACCOUNT_CONFIG_STATUS, db_column='status', default=0)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name='package', db_column='package')
    created = models.DateTimeField(auto_now_add=True, db_column='created')
    updated = models.DateTimeField(auto_now=True, db_column='updated')

    class Meta:
        managed = True
        db_table = 'account_config'
