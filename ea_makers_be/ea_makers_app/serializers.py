from rest_framework import serializers
from utils.zalo import ZaloOA
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

    def create(self, validated_data):
        zalo_oa = ZaloOA()
        transaction = Transaction.objects.create(**validated_data)
        type = ""
        path = ""
        if transaction.type is 0:
            path = "duyetnaptien"
            type = "Nạp tiền"
        elif transaction.type is 1:
            path = "duyetruttien"
            type = "Rút tiền"
        message = "Tài khoản Lead {} vừa gửi yêu cầu {}. Vui lòng vào kiểm tra tại https://eamakers.com/admin/dieukhienhethong/{}".format(
            transaction.user.fullname, type, path)
        # Gui Tin nhan cho Admin
        admins = User.objects.filter(is_admin=True)
        for admin in admins:
            zalo_id = admin.zalo_id
            if zalo_id is not None and type != "" and path != "":
                print("Sent message to zalo")
                res = zalo_oa.sent_text_message(zalo_id, message)
                print(res.text)
        return transaction

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
    account_details = AccountMT4Serializer(source='account', read_only=True)

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
