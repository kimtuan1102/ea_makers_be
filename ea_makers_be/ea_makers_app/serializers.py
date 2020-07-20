from rest_framework import serializers

from ea_makers_be.ea_makers_app.models import User


# Main Model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name']


