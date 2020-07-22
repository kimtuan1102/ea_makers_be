# Create your views here.
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Transaction, ServerInfo, Office, AccountMT4, AccountHistory, Package, AccountConfig
from .serializers import TransactionSerializer, ServerInfoSerializer, OfficeSerializer, AccountMT4Serializer, \
    AccountHistorySerializer, PackageSerializer, AccountConfigSerializer


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        return Transaction.objects.all()


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
