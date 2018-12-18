from django.contrib.auth import authenticate
from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers, exceptions
from rest_auth.registration.serializers import RegisterSerializer

from .models import User, AuthorizationToken


class AuthorizationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuthorizationToken
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    auth_tokens = AuthorizationTokenSerializer(read_only=True, many=True)

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'user_type', 'auth_tokens', 'date_joined')
        read_only_fields = ('email',)


class UserRegistrationSerializer(RegisterSerializer):
    name = serializers.CharField(max_length=64)
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    user_type = serializers.CharField(max_length=3)

    def get_cleaned_data(self):
        return {
            'name': self.validated_data.get('name', ''),
            'password1': self.validated_data.get('password1', ''),
            'email': self.validated_data.get('email', ''),
            'user_type': self.validated_data.get('user_type', ''),
        }


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, allow_blank=False)
    password = serializers.CharField(style={'input_type': 'password'})

    def _validate_email(self, email, password):
        user = None
        if email and password:
            user = authenticate(email=email, password=password)
        else:
            msg = _('Must include "email" and "password".')
            raise exceptions.ValidationError(msg)
        return user

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        user = None

        if 'allauth' in settings.INSTALLED_APPS:
            from allauth.account import app_settings

            # Authentication through email
            if app_settings.AUTHENTICATION_METHOD == app_settings.AuthenticationMethod.EMAIL:
                user = self._validate_email(email, password)

        # Did we get back an active user?
        if user:
            if not user.is_active:
                msg = _('User account is disabled.')
                raise exceptions.ValidationError(msg)
        else:
            msg = _('Unable to log in with provided credentials.')
            raise exceptions.ValidationError(msg)

        # If required, is the email verified?
        if 'rest_auth.registration' in settings.INSTALLED_APPS:
            from allauth.account import app_settings
            if app_settings.EMAIL_VERIFICATION == app_settings.EmailVerificationMethod.MANDATORY:
                email_address = user.emailaddress_set.get(email=user.email)
                if not email_address.verified:
                    raise serializers.ValidationError(_('E-mail is not verified.'))

        attrs['user'] = user
        return attrs
