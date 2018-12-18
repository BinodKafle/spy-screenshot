import datetime

from rest_auth.registration.views import RegisterView, VerifyEmailView
from rest_auth.views import LoginView

from .serializers import UserRegistrationSerializer, LoginSerializer

from .models import AuthorizationToken
from .serializers import AuthorizationTokenSerializer

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout as django_logout

from allauth.account import app_settings as allauth_settings
from allauth.account.utils import complete_signup

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status


class VerifyEmailRegisterView(VerifyEmailView):
    serializer_class = VerifyEmailView

    def post(self, request, *args, **kwargs):
        response = super(VerifyEmailRegisterView, self).post(
            request, *args, **kwargs)
        response.data = {
            "code": getattr(settings, 'SUCCESS_CODE', 1),
            "message": "Email Successfully verified."
        }
        return response


class RegisterUserView(RegisterView):
    serializer_class = UserRegistrationSerializer
    token_model = AuthorizationToken

    def get_response_data(self, user):
        if allauth_settings.EMAIL_VERIFICATION == \
                allauth_settings.EmailVerificationMethod.MANDATORY:
            data = {
                'code': getattr(settings, 'SUCCESS_CODE', 1),
                'message': "Please check your email for account validation link. Thank you.",
            }
            return data

    def perform_create(self, serializer):
        user = serializer.save(self.request)

        complete_signup(self.request._request, user,
                        allauth_settings.EMAIL_VERIFICATION,
                        None)
        return user


class Login(LoginView):
    serializer_class = LoginSerializer
    token_model = AuthorizationToken

    def create_token(self):
        token = self.token_model.objects.get_or_create(user=self.user)
        return token

    def get_response_serializer(self):
        response_serializer = AuthorizationTokenSerializer
        return response_serializer

    def post(self, request, *args, **kwargs):
        self.request = request
        self.serializer = self.get_serializer(data=self.request.data,
                                              context={'request': request})
        self.serializer.is_valid(raise_exception=True)
        first_login = False if self.serializer.validated_data['user'].last_login else True
        self.login()
        self.user.last_login = datetime.datetime.now()
        self.user.save()
        response = self.get_response()

        print(response.data)
        response.data = {
            'code': getattr(settings, 'SUCCESS_CODE', 1),
            'message': "Successfully Logged In.",
            'data': {
                'id': self.user.id,
                'name': self.user.name,
                'is_first_login': first_login,
                'user_type': self.user.user_type
            }
        }
        return response


def get_token_obj(token):
    return AuthorizationToken.objects.get(key=token)


@api_view(['POST'])
def logout(request):
    """
    Calls Django logout method and delete the Token object
    assigned to the current User object.

    Accepts/Returns nothing.
    """
    try:
        AuthorizationToken.objects.filter(key=request.auth).delete()
    except (AttributeError, ObjectDoesNotExist) as err:
        return Response({
            "code": getattr(settings, 'ERROR_CODE', 0),
            "message": str(err)},
            status=status.HTTP_400_BAD_REQUEST)

    django_logout(request)
    return Response({"code": getattr(settings, 'SUCCESS_CODE', 1), "message": "Successfully logged out."},
                    status=status.HTTP_200_OK)

