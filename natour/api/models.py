"""
Entity creation file
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import AbstractUser


class Role(models.Model):
    """
    Model representing a user role.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        """
        Meta options for the Role model.
        """
        ordering = ["name"]
        verbose_name = "Role"
        verbose_name_plural = "Roles"


class CustomUser(AbstractUser):
    """
    Custom user model that extends the default Django user model.
    """
    id = models.AutoField(primary_key=True)
    role = models.ForeignKey(
        Role,
        default=1,
        on_delete=models.SET_NULL,
        related_name="users",
        blank=False,
        null=False)
    email = models.EmailField(unique=True)
    deactivation_reson = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email

    class Meta:
        """
        Meta options for the CustomUser model.
        """
        ordering = ["id"]
        verbose_name = "User"
        verbose_name_plural = "Users"


class PointTypes(models.TextChoices):
    """
    Enum representing different types of points.
    """
    TRAIL = 'trail', 'Trilha'
    WATER_FALL = 'water_fall', 'Cachoeira'
    PARK = 'park', 'Parque'
    FARM = 'farm', 'Fazenda'
    OTHER = 'other', 'Outro'


class Point(models.Model):
    """
    Model representing a point in the system.
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="points",
        blank=False,
        null=False
    )
    name = models.CharField(max_length=100, unique=False)
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=False, null=False)
    week_start = models.DateField(blank=False, null=False)
    week_end = models.DateField(blank=False, null=False)
    open_time = models.TimeField(blank=False, null=False)
    close_time = models.TimeField(blank=False, null=False)
    point_type = models.CharField(
        choices=PointTypes.choices,
        default=PointTypes.OTHER
    )
    link = models.URLField(blank=True, null=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    zip_code = models.CharField(max_length=20, blank=False, null=False)
    city = models.CharField(max_length=100, blank=False, null=False)
    neighborhood = models.CharField(max_length=100, blank=False, null=False)
    state = models.CharField(max_length=100, blank=False, null=False)
    street = models.CharField(max_length=200, blank=False, null=False)
    number = models.CharField(max_length=20, blank=False, null=False)
    # photos = models.ImageField(
    #     upload_to="points_photos/",
    #     blank=True,
    #     null=True
    # )
    deactivation_reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    class Meta:
        """
        Meta options for the Point model.
        """
        ordering = ["name"]
        verbose_name = "Point"
        verbose_name_plural = "Points"


class PointReview(models.Model):
    """
    Model representing a review for a point.
    """
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="reviews",
        blank=False,
        null=False
    )
    point = models.ForeignKey(
        Point,
        on_delete=models.CASCADE,
        related_name="reviews",
        blank=False,
        null=False
    )
    rating = models.IntegerField(blank=False, null=False, validators=[
        MinValueValidator(1),
        MaxValueValidator(5)
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Review by {self.user} for {self.point} with rating {self.rating}"

    class Meta:
        """
        Meta options for the PointReview model.
        """
        ordering = ["-created_at"]
        verbose_name = "Point Review"
        verbose_name_plural = "Point Reviews"


class Terms(models.Model):
    """
    Model representing the terms and policy of the plataform.
    """
    id = models.AutoField(primary_key=True)
    content = models.TextField(blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.content)

    class Meta:
        """
        Meta options for the Terms model.
        """
        ordering = ["-created_at"]
        verbose_name = "Term"
        verbose_name_plural = "Terms"
