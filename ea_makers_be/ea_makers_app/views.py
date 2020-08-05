# Create your views here.
from django.utils import timezone
import json
from json import JSONDecodeError

from django.db import IntegrityError
from django.db.models import F
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from utils.zalo import ZaloOA
from .filters import TransactionFilter
from .models import Transaction, ServerInfo, Office, AccountMT4, AccountHistory, Package, AccountConfig, User, \
    CustomCache
from .serializers import TransactionSerializer, ServerInfoSerializer, OfficeSerializer, AccountMT4Serializer, \
    AccountHistorySerializer, PackageSerializer, AccountConfigSerializer, UserSerializer, ChangePasswordSerializer
from .permissions import TransactionPermission, IsAdminPermission, AccountConfigPermission, IsSuperUserPermission, \
    IsLeadPermission, IsMT4Permission


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [TransactionPermission]
    authentication_classes = (JWTAuthentication,)
    filter_class = TransactionFilter

    def get_queryset(self):
        if self.request.user.is_anonymous is not True:
            if self.request.user.is_lead is True:
                return Transaction.objects.filter(user_id=self.request.user.id)
        return Transaction.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AccountMT4ViewSet(viewsets.ModelViewSet):
    queryset = AccountMT4.objects.all()
    serializer_class = AccountMT4Serializer
    authentication_classes = (JWTAuthentication,)


class AccountHistoryViewSet(viewsets.ModelViewSet):
    queryset = AccountHistory.objects.all()
    serializer_class = AccountHistorySerializer
    authentication_classes = (JWTAuthentication,)


class AccountConfigViewSet(viewsets.ModelViewSet):
    queryset = AccountConfig.objects.all()
    serializer_class = AccountConfigSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_anonymous is not True:
            if self.request.user.is_admin is True or self.request.user.is_superuser:
                return AccountConfig.objects.all()
            else:
                return AccountConfig.objects.filter(user_id=self.request.user.id)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAuthenticated]


class ServerInfoViewSet(viewsets.ModelViewSet):
    queryset = ServerInfo.objects.all()
    serializer_class = ServerInfoSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAuthenticated]


class OfficeViewSet(viewsets.ModelViewSet):
    queryset = Office.objects.all()
    serializer_class = OfficeSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = [IsAuthenticated]


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def transaction_approve(request, id):
    #
    try:
        transaction = Transaction.objects.get(id=id)
        user = transaction.user
        # Chỉ Approve khi trạng thái là pending
        if transaction.status is 0:
            # Xử lý khi lead nạp tiền
            if transaction.type is 0:
                # Cộng tiền cho lead
                user.balance = user.balance + transaction.amount
                user.save()
                # Cập nhật trạng thái transaction
                transaction.status = 1
                transaction.save()
                return Response({'code': 200, 'message': 'Approve transaction success'})
            # Xử lý khi người dùng rút tiền
            elif transaction.type is 1:
                # Kiểm tra tài khoản
                if user.balance < transaction.amount:
                    return Response({'code': 400, 'message': 'Not enough money'})
                else:
                    # Trừ tiền và success
                    user.balance = user.balance - transaction.amount
                    user.save()
                    transaction.status = 1
                    transaction.save()
                    return Response({'code': 200, 'message': 'Approve transaction success'})
        return Response({'code': 400, 'message': 'Status is not pending or invalid transaction type'})
    except Transaction.DoesNotExist:
        return Response({'code': 404, 'message': 'transaction does not exists'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def transaction_reject(request, id):
    try:
        Transaction.objects.filter(id=id).update(status=2)
        return Response({'code': 200, 'message': 'Reject transaction success'})
    except Transaction.DoesNotExist:
        return Response({'code': 404, 'message': 'transaction does not exists'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticated])
def user_info(request):
    try:
        user = User.objects.get(pk=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)

    except User.DoesNotExist:
        return Response({'code': 404, 'message': 'User does not exists'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
def ea_license(request, id):
    try:
        key_license = str(id) + '_license'
        custom_cache = CustomCache.objects.get(key=key_license)
        exp_license = custom_cache.expired_time
        if exp_license < timezone.now():
            return Response({'code': 401, 'message': 'License expired'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            account = AccountConfig.objects.get(account__id=id)
            if account.status is 2:
                return Response({'is_verified': True, 'percent': account.percent_copy, 'parent_id': account.parent.id},
                                status=status.HTTP_200_OK)
            else:
                return Response({'code': 400, 'message': 'Status not is running'}, status=status.HTTP_400_BAD_REQUEST)

    except AccountConfig.DoesNotExist:
        return Response({'code': 404, 'message': 'User does not exists'}, status=status.HTTP_404_NOT_FOUND)
    except CustomCache.DoesNotExist:
        return Response({'code': 401, 'message': 'Does not have license'}, status=status.HTTP_401_UNAUTHORIZED)


# Admin duyệt tạo máy
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def account_config_admin_approve(request, id):
    # Cập nhật trạng thái và tài khoản master
    custom_cache = CustomCache()
    try:
        body = json.loads(request.body.decode('utf-8'))
        parent = body['parent']
        account_config = AccountConfig.objects.get(pk=id)
        if account_config.status is 1:
            return Response({'code': 400, 'message': 'Trạng thái không hợp lệ'}, status.HTTP_400_BAD_REQUEST)
        account_config.status = 1
        account_config.parent = AccountMT4.objects.get(pk=parent)
        user = account_config.user
        commission = account_config.package.commission * account_config.package.price / 100
        price = account_config.package.price
        # Kiểm tra tài khoản
        if user.balance < price:
            return Response({'code': 400, 'message': 'Tài khoản không đủ tiền thanh toán'})
        else:
            # Trừ tiền và success
            # Ban ghi mua goi
            Transaction.objects.create(user=user, type=3, amount=price, status=1)
            # Ban ghi hoa hong
            Transaction.objects.create(user=user, type=2, amount=commission, status=1)
            user.balance = user.balance - price + commission
            user.save()
            account_config.save()
            # Tao ban ghi transaction
            exp = account_config.package.month * 30 * 24 * 3600
            # Lưu thời hạn bảo lãnh
            if account_config.package.month >= 3:
                key_guarantee = str(account_config.account.id) + '_guarantee'
                exp_guarantee = 30 * 24 * 3600
                custom_cache.set(key_guarantee, exp_guarantee)
            # Thời hạn license
            key_license = str(account_config.account.id) + '_license'
            custom_cache.set(key_license, exp)
            return Response({'code': 200, 'message': 'Success'})
    except AccountConfig.DoesNotExist:
        return Response({'code': 400, 'message': 'Id không hợp lệ. Dữ liệu cấu hình không tồn tại'},
                        status.HTTP_400_BAD_REQUEST)
    except KeyError:
        return Response({'code': 400, 'message': 'Thiếu trường thông tin'}, status.HTTP_400_BAD_REQUEST)
    except JSONDecodeError:
        return Response({'code': 400, 'message': 'Thiếu gói tin body'}, status.HTTP_400_BAD_REQUEST)


# Admin hủy config
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def account_config_admin_reject(request, id):
    try:
        AccountConfig.objects.filter(pk=id).update(status=4)
        return Response({'code': 200, 'message': 'Success'})
    except AccountConfig.DoesNotExist:
        return Response({'code': 404, 'message': 'Account config does not exist'}, status=status.HTTP_400_BAD_REQUEST)


# Super admin xác nhận đã tạo máy
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsSuperUserPermission])
def account_config_superadmin_approve(request, id):
    try:
        body = json.loads(request.body.decode('utf-8'))
        account_config = AccountConfig.objects.get(pk=id)
        if account_config.status is not 1:
            return Response({'code': 400, 'message': 'Status is not creating'}, status.HTTP_400_BAD_REQUEST)
        server = body['server']
        if server is None:
            return Response({'code': 400, 'message': 'Missing parent field'}, status.HTTP_400_BAD_REQUEST)
        else:
            # Cập nhật thông tin server
            account_config.status = 2
            account_config.server = ServerInfo.objects.get(pk=server)
            account_config.save()
            # Cộng tiền cho super admin
            price = 30 + (account_config.package.month - 1) * 25
            User.objects.filter(is_superuser=True).update(balance=F('balance') + price)
            return Response({'code': 200, 'message': 'Success'}, status.HTTP_200_OK)
    except AccountConfig.DoesNotExist:
        return Response({'code': 404, 'message': 'Account config does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    except ServerInfo.DoesNotExist:
        return Response({'code': 404, 'message': 'Server info does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    except JSONDecodeError:
        return Response({'code': 400, 'message': 'Body data is invalid'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsLeadPermission])
def create_order(request):
    try:
        zalo_oa = ZaloOA()
        body = json.loads(request.body.decode('utf-8'))
        id = body['id']
        pwd = body['pwd']
        name = body['name']
        office = body['office']
        package = body['package']
        percent_copy = body['percent_copy']
        office_instance = Office.objects.get(pk=office)
        package_instance = Package.objects.get(pk=package)
        # Tạo tài khoản cho khách đăng nhập
        account_mt4 = AccountMT4.objects.create(id=id, pwd=pwd, name=name, office=office_instance, owner=request.user)
        User.objects.create_user(account_mt4.id, account_mt4.name, account_mt4.pwd, )
        # Ban ghi account config
        AccountConfig.objects.create(user=request.user, account=account_mt4, package=package_instance,
                                     percent_copy=percent_copy)
        # Gửi tin nhắn zalo cho admin
        admins = User.objects.filter(is_admin=True)
        message = "Tài khoản Lead {} vừa gửi yêu cầu {}. Vui lòng vào kiểm tra tại https://eamakers.com/admin/dieukhienhethong/{}".format(
            request.user.fullname, "Mua bot", "duyetmuabot")
        for admin in admins:
            zalo_id = admin.zalo_id
            if zalo_id is not None:
                print("Sent message to zalo")
                res = zalo_oa.sent_text_message(zalo_id, message)
                print(res.text)
        return Response({'code': 200, 'message': 'Tạo order thành công'}, status.HTTP_200_OK)
    except Office.DoesNotExist:
        return Response({'code': 400, 'message': 'Thông tin văn phòng không chính xác'}, status.HTTP_400_BAD_REQUEST)
    except Package.DoesNotExist:
        return Response({'code': 404, 'message': 'Thông tin gói không chính xác'}, status.HTTP_400_BAD_REQUEST)
    except KeyError:
        return Response({'code': 400, 'message': 'Thiếu trường thông tin'}, status.HTTP_400_BAD_REQUEST)
    except JSONDecodeError:
        return Response({'code': 400, 'message': 'Thiếu gói tin body'}, status.HTTP_400_BAD_REQUEST)
    except IntegrityError:
        return Response({'code': 400, 'message': 'Tài khoản MT4 đã tồn tại. Vui lòng chọn gia hạn.'},
                        status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsLeadPermission])
def extension_order(request, id):
    custom_cache = CustomCache()
    try:
        body = json.loads(request.body.decode('utf-8'))
        package = body['package']
        package_instance = Package.objects.get(pk=package)
        price = package_instance.price
        commission = package_instance.commission * package_instance.price / 100
        account_config = AccountConfig.objects.get(pk=id)
        user = account_config.user
        if account_config.status is not 2:
            return Response({'code': 400, 'message': 'Trạng thái không hợp lệ'}, status.HTTP_400_BAD_REQUEST)
        # Kiểm tra tài khoản
        if user.balance < price:
            return Response({'code': 400, 'message': 'Tài khoản không đủ tiền thanh toán'})
        # Trừ tiền lead và success
        # Ban ghi mua goi
        Transaction.objects.create(user=user, type=3, amount=price, status=1)
        # Ban ghi hoa hong
        Transaction.objects.create(user=user, type=2, amount=commission, status=1)
        user.balance = user.balance - price + commission
        user.save()
        money = 30 + (package_instance.month - 1) * 25
        # Cộng tiền cho superuser
        User.objects.filter(is_superuser=True).update(balance=F('balance') + money)
        account_config.package = package_instance
        account_config.save()
        # Cập nhật license
        exp = package_instance.month * 30 * 24 * 3600
        # Lưu thời hạn bảo lãnh
        if package_instance.month >= 3:
            key_guarantee = str(account_config.account.id) + '_guarantee'
            exp_guarantee = 30 * 24 * 3600
            custom_cache.set(key_guarantee, exp_guarantee)
        # Thời hạn license
        key_license = str(account_config.account.id) + '_license'
        custom_cache.set(key_license, exp)
        return Response({'code': 200, 'message': 'Gia hạn thành công.'}, status.HTTP_200_OK)
    except KeyError:
        return Response({'code': 400, 'message': 'Thiếu trường thông tin'}, status.HTTP_400_BAD_REQUEST)
    except JSONDecodeError:
        return Response({'code': 400, 'message': 'Thiếu gói tin body'}, status.HTTP_400_BAD_REQUEST)
    except Package.DoesNotExist:
        return Response({'code': 400, 'message': 'Gói gia hạn không hợp lệ'}, status.HTTP_400_BAD_REQUEST)
    except AccountConfig.DoesNotExist:
        return Response({'code': 400, 'message': 'Id không hợp lệ. Dữ liệu cấu hình không tồn tại'},
                        status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsMT4Permission])
def license_time(request):
    try:
        license_key = request.user.username + '_license'
        custom_cache = CustomCache.objects.get(key=license_key)
        return Response({'expired_time': custom_cache.expired_time})
    except CustomCache.DoesNotExist:
        return Response({'code': 404, 'message': 'Bạn chưa có license.'},
                        status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsMT4Permission])
def guarantee_time(request):
    try:
        guarantee_key = request.user.username + '_guarantee'
        custom_cache = CustomCache.objects.get(key=guarantee_key)
        return Response({'expired_time': custom_cache.expired_time})
    except CustomCache.DoesNotExist:
        return Response({'code': 404, 'message': 'Bạn chưa có bảo lãnh.'},
                        status.HTTP_200_OK)


class ChangePasswordView(UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
