from rest_framework import serializers

from ea_copy_be.ea_copy_be_app.models import User, AccountMT4


# Main Model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']


# App Model
class AccountMT4Serializer(serializers.ModelSerializer):
    class Meta:
        model = AccountMT4
        fields = ['name', 'is_parent', 'description']

