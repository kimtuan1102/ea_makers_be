# Create your views here.
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Transaction, ServerInfo, Office, AccountMT4, AccountHistory, Package, AccountConfig, User
from .serializers import TransactionSerializer, ServerInfoSerializer, OfficeSerializer, AccountMT4Serializer, \
    AccountHistorySerializer, PackageSerializer, AccountConfigSerializer
from .permissions import TransactionPermission, IsAdminPermission


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


class ServerInfoViewSet(viewsets.ModelViewSet):
    queryset = ServerInfo.objects.all()
    serializer_class = ServerInfoSerializer
    authentication_classes = (JWTAuthentication,)


class OfficeViewSet(viewsets.ModelViewSet):
    queryset = Office.objects.all()
    serializer_class = OfficeSerializer
    authentication_classes = (JWTAuthentication,)


class AccountMT4ViewSet(viewsets.ModelViewSet):
    queryset = AccountMT4.objects.all()
    serializer_class = AccountMT4Serializer
    authentication_classes = (JWTAuthentication,)


class AccountHistoryViewSet(viewsets.ModelViewSet):
    queryset = AccountHistory.objects.all()
    serializer_class = AccountHistorySerializer
    authentication_classes = (JWTAuthentication,)


class PackageViewSet(viewsets.ModelViewSet):
    queryset = Package.objects.all()
    serializer_class = PackageSerializer
    authentication_classes = (JWTAuthentication,)


class AccountConfigViewSet(viewsets.ModelViewSet):
    queryset = AccountConfig.objects.all()
    serializer_class = AccountConfigSerializer
    authentication_classes = (JWTAuthentication,)


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
                # Cập nhật trạng thái transaction
                transaction.status = 1
                transaction.save()
            # Xử lý khi người dùng rút tiền
            elif transaction.type is 1:
                # Kiểm tra tài khoản
                if user.balance < transaction.amount:
                    return Response({'code': 400, 'message': 'Not enough money'})
                else:
                    # Trừ tiền và success
                    user.balance = user.balance - transaction.amount
                    return Response({'code': 200, 'message': 'Approve transaction success'})
            # Tiền hoa hồng
            elif transaction.type is 2:
                # Cộng tiền và success
                user.balance = user.balance + transaction.amount
                return Response({'code': 200, 'message': 'Approve transaction success'})
            # Mua gói
            elif transaction.type is 3:
                # Kiểm tra tài khoản
                if user.balance < transaction.amount:
                    return Response({'code': 400, 'message': 'Not enough money'})
                else:
                    # Trừ tiền lead và success
                    user.balance = user.balance - transaction.amount
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
