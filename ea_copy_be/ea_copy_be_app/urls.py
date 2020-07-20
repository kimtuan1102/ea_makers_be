from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ea_copy_be.ea_copy_be_app.views import AccountMT4ViewSet

router = DefaultRouter()
router.register(r'account-mt4', AccountMT4ViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]