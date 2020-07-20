# Create your views here.
from rest_framework import viewsets

from ea_copy_be.ea_copy_be_app.models import AccountMT4
from ea_copy_be.ea_copy_be_app.serializers import AccountMT4Serializer


class AccountMT4ViewSet(viewsets.ModelViewSet):
    queryset = AccountMT4.objects.all()
    serializer_class = AccountMT4Serializer
