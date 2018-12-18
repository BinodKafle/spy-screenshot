from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
import binascii, os

from .managers import UserManager

USER_TYPE_ADMIN = 1
USER_TYPE_NUSER = 2
USER_TYPE_CHOICES = (
    (1, 'admin'),
    (2, 'user')
)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=255, default='')
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.PositiveSmallIntegerField(choices=USER_TYPE_CHOICES, default=2)
    date_joined = models.DateTimeField(_('date_joined'), auto_now_add=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    def __str__(self):
        return self.email


class AuthorizationToken(models.Model):
    key = models.CharField(_('Key'), max_length=40, primary_key=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auth_tokens")
    user_type = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = _("Token")
        verbose_name_plural = _("Tokens")

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    def generate_key(self):
        return binascii.hexlify(os.urandom(20)).decode()

    def __str__(self):
        return self.key
