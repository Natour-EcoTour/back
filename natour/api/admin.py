"""
Module for Django admin registration of models.
"""
from django.contrib import admin
from .models import Role, CustomUser, Point, PointReview, Terms

# Basic registration
admin.site.register(Role)
admin.site.register(CustomUser)
admin.site.register(Point)
admin.site.register(PointReview)
admin.site.register(Terms)
