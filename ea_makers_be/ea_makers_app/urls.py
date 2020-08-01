from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TransactionViewSet, AccountMT4ViewSet, AccountHistoryViewSet, \
    AccountConfigViewSet, transaction_approve, transaction_reject, user_info, ea_license, PackageViewSet, \
    ServerInfoViewSet, account_config_admin_approve, account_config_admin_reject, create_order, \
    account_config_superadmin_approve, account_config_superadmin_reject, OfficeViewSet, extension_order, license_time, \
    guarantee_time, ChangePasswordView

router = DefaultRouter()
router.register(r'transaction', TransactionViewSet)
router.register(r'account-mt4', AccountMT4ViewSet)
router.register(r'account-history', AccountHistoryViewSet)
router.register(r'account-config', AccountConfigViewSet)
router.register(r'package', PackageViewSet)
router.register(r'server-info', ServerInfoViewSet)
router.register(r'office', OfficeViewSet)
urlpatterns = [
    path('api/', include(router.urls)),
    path(r'api/transaction/approve/<int:id>', transaction_approve),
    path(r'api/transaction/reject/<int:id>', transaction_reject),
    path(r'api/user-info', user_info),
    path(r'api/ea-license/<int:id>', ea_license),
    path(r'api/account-config/admin-approve/<int:id>', account_config_admin_approve),
    path(r'api/account-config/admin-reject/<int:id>', account_config_admin_reject),
    path(r'api/account-config/super-admin-reject/<int:id>', account_config_superadmin_reject),
    path(r'api/account-config/superadmin-approve/<int:id>', account_config_superadmin_approve),
    path(r'api/create-order', create_order),
    path(r'api/extension-order', extension_order),
    path(r'api/license-time', license_time),
    path(r'api/guarantee-time', guarantee_time),
    path(r'api/change-password', ChangePasswordView)
]
