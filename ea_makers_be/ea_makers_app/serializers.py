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
    class Meta:
        model = AccountMT4
        fields = '__all__'


class AccountHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountHistory
        fields = '__all__'


class PackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Package
        fields = '__all__'


class AccountConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountConfig
        fields = '__all__'
