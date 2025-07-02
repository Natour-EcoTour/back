"""
Module for Django admin registration of models.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Role, CustomUser, Point, PointReview, Terms, Photo

# Basic registration
admin.site.register(Role)
# admin.site.register(CustomUser)
admin.site.register(Point)
admin.site.register(PointReview)
admin.site.register(Terms)
admin.site.register(Photo)


class PointInline(admin.TabularInline):
    """
    Inline admin interface for Point model within CustomUser admin.

    Displays points created by a user as a tabular inline with clickable links
    to edit each point.
    """
    model = Point
    fields = ['link_to_point']
    readonly_fields = ['link_to_point']
    extra = 0

    def link_to_point(self, obj):
        """
        Create a clickable HTML link to the Point admin change page.

        Args:
            obj (Point): The Point model instance

        Returns:
            str: HTML formatted link to the point's admin page, or empty string if no ID
        """
        if obj.id:
            return format_html(
                '<a href="/admin/api/point/{}/change/">{}</a>', obj.id, obj.name
            )
        return ""
    link_to_point.short_description = "Point"


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    """
    Custom admin interface for CustomUser model.

    Provides enhanced admin functionality including:
    - Inline display of user's points
    - List view with email, role, and active status
    - Search functionality by email
    - Filtering by active status
    """
    inlines = [PointInline]
    list_display = ('email', 'role', 'is_active')
    search_fields = ('email',)
    list_filter = ('is_active',)
