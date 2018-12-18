from django.urls import include, path, re_path
from users.views import Login, logout, RegisterUserView, VerifyEmailRegisterView

urlpatterns = [
    path('login/', Login.as_view(), name='user_login'),
    path('logout/', logout, name='user_logout'),

    path('register/', RegisterUserView.as_view(), name='user_registration'),
    path('register/verify-email/', VerifyEmailRegisterView.as_view(), name="verify_email"),
    re_path('account-confirm-email/', VerifyEmailRegisterView.as_view(),
            name='account_email_verification_sent'),
]