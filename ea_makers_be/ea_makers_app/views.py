# Create your views here.
import json

from django.db.models import F
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.cache import cache

from .models import Transaction, ServerInfo, Office, AccountMT4, AccountHistory, Package, AccountConfig, User
from .serializers import TransactionSerializer, ServerInfoSerializer, OfficeSerializer, AccountMT4Serializer, \
    AccountHistorySerializer, PackageSerializer, AccountConfigSerializer, UserSerializer
from .permissions import TransactionPermission, IsAdminPermission, AccountConfigPermission, IsSuperUserPermission


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [TransactionPermission]
    authentication_classes = (JWTAuthentication,)

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
    permission_classes = [AccountConfigPermission]

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
                    return Response({'code': 200, 'message': 'Approve transaction success'})
            # Tiền hoa hồng
            elif transaction.type is 2:
                # Cộng tiền và success
                user.balance = user.balance + transaction.amount
                user.save()
                return Response({'code': 200, 'message': 'Approve transaction success'})
            # Mua gói
            elif transaction.type is 3:
                # Kiểm tra tài khoản
                if user.balance < transaction.amount:
                    return Response({'code': 400, 'message': 'Not enough money'})
                else:
                    # Trừ tiền lead và success
                    user.balance = user.balance - transaction.amount
                    user.save()
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
        if cache.get(id) is None:
            return Response({'code': 404, 'message': 'User does not exists'}, status=status.HTTP_404_NOT_FOUND)
        else:
            account = AccountConfig.objects.get(account__id=id)
            if account.status is 2:
                return Response({'is_verified': True, 'percent': account.percent_copy, 'parent_id': account.parent.id},
                                status=status.HTTP_200_OK)
            else:
                return Response({'code': 400, 'message': 'Status not is runing'}, status=status.HTTP_400_BAD_REQUEST)

    except AccountConfig.DoesNotExist:
        return Response({'code': 404, 'message': 'User does not exists'}, status=status.HTTP_404_NOT_FOUND)


# Admin duyệt tạo máy
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def account_config_create(request, id):
    # validate body
    if request.body is None:
        return Response({'code': 400, 'message': 'Missing body data'}, status.HTTP_400_BAD_REQUEST)
    body = json.loads(request.body.decode('utf-8'))
    parent = body['parent']
    if parent is None:
        return Response({'code': 400, 'message': 'Missing parent field'}, status.HTTP_400_BAD_REQUEST)
    else:
        # Cập nhật trạng thái và tài khoản master
        account_config = AccountConfig.objects.get(pk=id)
        account_config.status = 1
        account_config.parent = AccountMT4.objects.get(pk=parent)
        account_config.save()
        # Tạo cache
        exp = account_config.package.month * 30 * 24 * 3600
        cache.set(account_config.account.id, 'xxxxx', exp);
        return Response({'code': 200, 'message': 'Success'})


# Admin hủy config
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def account_config_reject(request, id):
    try:
        AccountConfig.objects.filter(pk=id).update(status=4)
        return Response({'code': 200, 'message': 'Success'})
    except AccountConfig.DoesNotExist:
        return Response({'code': 404, 'message': 'Account config does not exist'}, status=status.HTTP_200_OK)


# Super admin xác nhận đã tạo máy
@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsSuperUserPermission])
def account_config_complete(request, id):
    if request.body is None:
        return Response({'code': 400, 'message': 'Missing body data'}, status.HTTP_400_BAD_REQUEST)
    account_config = AccountConfig.objects.get(pk=id)
    if account_config.status is not 1:
        return Response({'code': 400, 'message': 'Status is not creating'}, status.HTTP_400_BAD_REQUEST)
    body = json.loads(request.body.decode('utf-8'))
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


@api_view(['POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAdminPermission])
def create_order(request):
    if request.body is None:
        return Response({'code': 400, 'message': 'Missing body data'}, status.HTTP_400_BAD_REQUEST)
    body = json.loads(request.body.decode('utf-8'))
    id = body['id', None]
    pwd = body['pwd', None]
    name = body['name', None]
    office = body['office', None]
    package = body['package', None]
    percent_copy = body['percent_copy', None]
    # Validate Input
    if id is None:
        return Response({'code': 400, 'message': 'Missing parent field id'}, status.HTTP_400_BAD_REQUEST)
    if pwd is None:
        return Response({'code': 400, 'message': 'Missing parent field pwd'}, status.HTTP_400_BAD_REQUEST)
    if name is None:
        return Response({'code': 400, 'message': 'Missing parent field name'}, status.HTTP_400_BAD_REQUEST)
    if office is None:
        return Response({'code': 400, 'message': 'Missing parent field office'}, status.HTTP_400_BAD_REQUEST)
    if package is None:
        return Response({'code': 400, 'message': 'Missing parent field package'}, status.HTTP_400_BAD_REQUEST)
    if percent_copy is None:
        return Response({'code': 400, 'message': 'Missing parent field percent_copy'}, status.HTTP_400_BAD_REQUEST)
    try:
        office_instance = Office.objects.get(pk=office)
        package_instance = Package.objects.get(pk=package)
        # Tạo tài khoản cho khách đăng nhập
        account_mt4 = AccountMT4.objects.create(id=id, pwd=pwd, name=name, office=office_instance,
                                                package=package_instance)
        User.objects.create_user(account_mt4.id, account_mt4.name, account_mt4.pwd)
        # Tao ban ghi transaction
        # Ban ghi mua goi
        Transaction.objects.create(user=request.user, type=3, amount=package.price)
        # Ban ghi hoa hong
        commission = package.commission * package.price * 100
        Transaction.objects.create(user=request.user, type=2, amount=commission)
        # Ban ghi account config
        AccountConfig.objects.create(user=request.user, account=account_mt4, package=package_instance,
                                     percent_copy=percent_copy)
    except Office.DoesNotExist:
        return Response({'code': 404, 'message': 'Office does not exist'}, status.HTTP_400_BAD_REQUEST)
    except Package.DoesNotExist:
        return Response({'code': 404, 'message': 'Package does not exist'}, status.HTTP_400_BAD_REQUEST)
