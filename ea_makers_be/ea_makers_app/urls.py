from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, AccountMT4ViewSet, AccountHistoryViewSet, \
    AccountConfigViewSet, transaction_approve, transaction_reject, user_info, ea_license, PackageViewSet, \
    ServerInfoViewSet, account_config_create, account_config_reject, create_order, account_config_complete

router = DefaultRouter()
router.register(r'transaction', TransactionViewSet)
router.register(r'account-mt4', AccountMT4ViewSet)
router.register(r'account-history', AccountHistoryViewSet)
router.register(r'account-config', AccountConfigViewSet)
router.register(r'package', PackageViewSet)
router.register(r'server-info', ServerInfoViewSet)
urlpatterns = [
    path('api/', include(router.urls)),
    path(r'api/transaction/approve/<int:id>', transaction_approve),
    path(r'api/transaction/reject/<int:id>', transaction_reject),
    path(r'api/user-info', user_info),
    path(r'api/ea-license/<int:id>', ea_license),
    path(r'api/account-config/create/<int:id>', account_config_create),
    path(r'api/account-config/reject/<int:id>', account_config_reject),
    path(r'api/account-config/complete/<int:id>', account_config_complete),
    path(r'api/create-order', create_order)
]
