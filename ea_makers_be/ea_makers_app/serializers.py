from rest_framework import serializers

from ea_makers_be.ea_makers_app.models import User, Transaction, ServerInfo, Office, AccountMT4, AccountHistory, \
    Package, AccountConfig


# Main Model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'fullname', 'balance']


class TransactionSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    status = serializers.ReadOnlyField()

    class Meta:
        model = Transaction
        fields = '__all__'


class ServerInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServerInfo
        fields = '__all__'


class OfficeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Office
        fields = '__all__'


class AccountMT4Serializer(serializers.ModelSerializer):
    is_parent = serializers.ReadOnlyField()

    def create(self, validated_data):
        # Tạo tài khoản cho khách đăng nhập
        account_mt4 = AccountMT4.objects.create(**validated_data)
        User.objects.create_user(account_mt4.id, account_mt4.name, account_mt4.pwd)
        return account_mt4

    class Meta:
        model = AccountMT4
        fields = '__all__'


class AccountHistorySerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='account.owner.id', read_only=True)

    class Meta:
        model = AccountHistory
        fields = '__all__'


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'


class AccountConfigSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    server = ServerInfoSerializer(read_only=True)

    class Meta:
        model = AccountConfig
        fields = '__all__'


class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
