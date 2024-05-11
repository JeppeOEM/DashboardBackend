"""
Database models.
"""
from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models


class Coin(models.Model):
    """Model for representing a coin."""
    name = models.CharField(max_length=255)
    # Other fields related to Coin model

    def __str__(self):
        return self.name


class Base(models.Model):
    """Model for representing a base currency."""
    name = models.CharField(max_length=255)
    # Other fields related to Coin model

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    """Manager for users."""

    def create_user(self, email, password=None, **extra_fields):
        """Create, save and return a new user."""
        if not email:
            raise ValueError('User must have an email address.')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser."""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """User in the system."""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    # check for admin rights
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Strategy(models.Model):
    """Strategy object."""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    base = models.ForeignKey(
        Coin,
        related_name='base_strategies',
        on_delete=models.CASCADE,
        null=True
    )
    coins = models.ManyToManyField('Coin')
    description = models.TextField(blank=True)
    tags = models.ManyToManyField('Tag')
    indicators = models.ManyToManyField('Indicator')

    def __str__(self):
        return self.title


class Grid(models.Model):
    """Indicator for strategies."""
    gridConfig = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    description = models.TextField()
    # description = models.TextField(blank=True)

    def __str__(self):
        return self.gridConfig


class Dashboard(models.Model):
    """Indicator for strategies."""
    gridConfig = models.TextField()
    gridConfig2 = models.TextField()
    gridConfig3 = models.TextField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    description = models.TextField()
    # description = models.TextField(blank=True)

    def __str__(self):
        return self.gridConfig


class Tag(models.Model):
    """Tag for filtering strategies."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name


class Indicator(models.Model):
    """Indicator for strategies."""
    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return self.name
