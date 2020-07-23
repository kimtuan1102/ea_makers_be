from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, ServerInfoViewSet, OfficeViewSet, AccountMT4ViewSet, AccountHistoryViewSet, \
    PackageViewSet, AccountConfigViewSet, transaction_approve, transaction_reject, user_info

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
    path(r'api/transaction/approve/<int:id>', transaction_approve),
    path(r'api/transaction/reject/<int:id>', transaction_reject),
    path(r'api/user-info', user_info)
]
