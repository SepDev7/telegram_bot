app_name = 'orders'

# orders/urls.py
from django.urls import path
from .views import CreateOrderView, CartView, RemoveOrderView, RegisterUserView, CheckVerificationView, external_configs_list
from . import views

urlpatterns = [
    path('register-user/', RegisterUserView.as_view()),
    path('check-verification/', CheckVerificationView.as_view()),
    path('create-order/', CreateOrderView.as_view()),
    path('cart/', CartView.as_view()),
    path('remove-order/', RemoveOrderView.as_view()),
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('admin-panel/toggle-verify/<int:user_id>/', views.toggle_verify, name='toggle_verify'),
    path('admin-panel/toggle-role/<int:user_id>/', views.toggle_role, name='toggle_role'),
    path('config-creator/', views.config_creator, name='config_creator'),
    path('configs-list/', views.configs_list, name='configs_list'),
    path('settings/', views.settings_panel, name='settings_panel'),
    path('settlement/', views.settlement_webapp, name='settlement_webapp'),
    path('admin-webapp/', views.admin_webapp, name='admin_webapp'),
    path('admin-api/users/', views.admin_users_list, name='admin_users_list'),
    path('admin-api/user-verify/', views.admin_user_verify, name='admin_user_verify'),
    path('admin-api/user-role/', views.admin_user_role, name='admin_user_role'),
    path('admin-api/user-delete/', views.admin_user_delete, name='admin_user_delete'),
    path('admin-api/user-balance/', views.admin_user_balance, name='admin_user_balance'),
    path('admin-receipts/', views.admin_receipts_list, name='admin_receipts_list'),
    path('webapp-data/', views.webapp_data_handler, name='webapp_data_handler'),
    path('upload-settlement-receipt/', views.upload_settlement_receipt, name='upload_settlement_receipt'),
    path('verify-receipt/', views.verify_receipt, name='verify_receipt'),
    path('wallet-to-wallet/', views.wallet_to_wallet_webapp, name='wallet_to_wallet_webapp'),
    path('wallet-to-wallet-transfer/', views.wallet_to_wallet_transfer, name='wallet_to_wallet_transfer'),
    path('rules/', views.rules_webapp, name='rules_webapp'),
    path('create-inbound/', views.create_inbound, name='create_inbound'),
    path('api-config-creator/', views.api_config_creator, name='api_config_creator'),
    path('user-dashboard/<str:user_code>/', views.user_dashboard, name='user_dashboard'),
    path('toggle-config-status/', views.toggle_config_status, name='toggle_config_status'),
    path('delete-config/', views.delete_config, name='delete_config'),
    path('upload-profile-picture/', views.upload_profile_picture, name='upload_profile_picture'),
    path('external-configs/', external_configs_list, name='external_configs_list'),
    path('report/', views.report_webapp, name='report_webapp'),
    path('submit-report/', views.submit_report, name='submit_report'),
    path('admin-reports/', views.admin_reports_list, name='admin_reports_list'),
    path('resolve-report/', views.resolve_report, name='resolve_report'),
    path('test-config-report/', views.test_config_report, name='test_config_report'),
]
