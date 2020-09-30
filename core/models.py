from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager, PermissionsMixin
from django.utils import timezone


class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """
        Creates and saves a new user.
        """
        if not email:
            raise ValueError("User must have an email address")
        user = self.model(
            email=self.normalize_email(email=email),
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create a new superuser"""
        user = self.create_user(email,password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model that supports using email instead of username.
    """
    email = models.EmailField(
        max_length=255,
        unique=True,
        help_text="Email Id of the user",
        verbose_name="Email Id",
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Name of the User",
        help_text="Name of the User",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Active",
        help_text="Designates whether this user should be treated as 'active'. Unselect this instead of deleting accounts."
    )
    is_staff = models.BooleanField(
        default=False,
        verbose_name="Staff status",
        help_text="Designates whether the user can log into this admin 'site'."
    )
    date_joined = models.DateTimeField(default=timezone.now)
    # is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    # REQUIRED_FIELDS = []

    def __str__(self):
        return self.name