from rest_framework_simplejwt.serializers import TokenObtainSerializer
from rest_framework_simplejwt.views import TokenObtainPairView


class CustomTokenObtainPairSerializer(TokenObtainSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add token claim
        token['email'] = user.email
        token['name'] = user.name


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
