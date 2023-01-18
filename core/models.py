# from django.db import models

# Create your models here.

from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models


class Otp(models.Model):
    country_code = models.CharField(
        max_length=5,
        blank=True,
        verbose_name="Country Code",
        help_text="standard country code extension",
    )
    phone_number = models.CharField(
        max_length=10,
        blank=False,
        verbose_name="Phone Number",
        help_text="10 digit valid phone number",
    )
    code = models.IntegerField(
        null=False, verbose_name="Text Code", help_text="6 digit unique code"
    )
    count = models.IntegerField(
        default=0,
        verbose_name="Retry Count",
        help_text="count of no of attempts made to send unique code",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return f"{self.phone_number}"


class CustomUser(AbstractBaseUser, PermissionsMixin):
    country_code = models.CharField(
        max_length=5,
        blank=True,
        verbose_name="Country Code",
        help_text="standard country code extension",
    )
    phone_number = models.CharField(
        max_length=10,
        blank=False,
        verbose_name="Phone Number",
        help_text="10 digit valid phone number",
        unique=True,
    )
    first_name = models.CharField(max_length=25, blank=True)
    middle_name = models.CharField(max_length=25, blank=True)
    last_name = models.CharField(max_length=25, blank=True)
    mpin_set = models.BooleanField(
        default=False, verbose_name="is_Mpin_Set", help_text="is Mpin set"
    )
    mpin = models.CharField(
        max_length=128,
        blank=True,
        verbose_name="User Mpin",
        help_text="Users secured code stored as hash",
    )
    kyc_verified = models.BooleanField(
        default=False, verbose_name="is_Kyc_Verified", help_text="is Mpin set"
    )

    (
        username,
        date_joined,
        last_login,
        is_superuser,
        is_staff,
        user_permissions,
        groups,
    ) = [None] * 7

    USERNAME_FIELD = "phone_number"

    def __str__(self):
        return f"{self.phone_number}"

    # Call to save the mpin as hash
    def set_mpin_hash(self, code):
        self.mpin = make_password(code)
        self.save()


class Tokens(models.Model):
    token_type_choices = [
        ("REFRESH", "Refresh Token Type"),
    ]
    token_type = models.CharField(
        max_length=10, choices=token_type_choices, default="REFRESH"
    )
    user_id = models.ForeignKey(
        CustomUser,
        related_name="user_token",
        verbose_name="User Token",
        on_delete=models.CASCADE,
        null=False,
        editable=False,
        blank=False,
    )
    token = models.CharField(
        max_length=128,
        blank=False,
        verbose_name="User Token",
        help_text="Users secured token",
    )
    expiry = models.DateTimeField(
        verbose_name="Token Expiry", help_text="Token expiry time"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return f"{self.token}"
