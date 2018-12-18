from rest_framework.authentication import TokenAuthentication
from users.models import AuthorizationToken


class MyOwnTokenAuthentication(TokenAuthentication):
    model = AuthorizationToken
