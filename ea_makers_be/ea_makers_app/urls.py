from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, ServerInfoViewSet, OfficeViewSet, AccountMT4ViewSet, AccountHistoryViewSet, \
    PackageViewSet, AccountConfigViewSet

router = DefaultRouter()
router.register(r'transaction', TransactionViewSet)
router.register(r'server-info', ServerInfoViewSet)
router.register(r'office', OfficeViewSet)
router.register(r'account-mt4', AccountMT4ViewSet)
router.register(r'account-history', AccountHistoryViewSet)
router.register(r'package', PackageViewSet)
router.register(r'account-config', AccountConfigViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
