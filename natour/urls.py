"""
URL configuration for natour project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from django_prometheus import exports

from .api.views.auth import MyTokenObtainPairView, create_user, login, get_refresh_token
from .api.views.users import (get_my_info, delete_my_account, update_my_info,
                              get_all_users, change_user_status, delete_user_account,
                              get_user_points, get_my_points, update_my_password)
from .api.views.photo import create_photo, update_photo, get_photo, delete_photo
from .api.views.terms import create_terms, get_terms, update_terms
from .api.views.point import (create_point, get_point_info, get_all_points,
                              change_point_status, delete_point, delete_my_point,
                              add_view, edit_point, point_approval, show_points_on_map)
from .api.views.review import add_review
from .api.views.code import (
    send_verification_code, verify_code, send_password_reset_code,
    verify_password_reset_code)

urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),

    path("metrics", exports.ExportToDjangoView, name="metrics"),

    # Auth URLs
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     path('token/get_refresh/', get_refresh_token, name='get_refresh_token'),

    # User management URLs
    path('users/login/', login, name='login'),
    path('users/create/', create_user, name='create_user'),
    path('users/me/', get_my_info, name='get_my_info'),
    path('users/me/update/', update_my_info, name='update_my_info'),
    path('users/me/delete/', delete_my_account, name='delete_my_account'),
    path('users/<int:user_id>/delete/',
         delete_user_account, name='delete_user_account'),
    path('users/list/', get_all_users, name='get_all_users'),
    path('users/<int:user_id>/status/',
         change_user_status, name='change_user_status'),
    path('users/<int:user_id>/points/', get_user_points, name='get_user_points'),
    path('users/me/points/', get_my_points, name='get_my_points'),
    path('users/me/update/password/',
         update_my_password, name='update_my_password'),

    # Code verification URL
    path('code/send/', send_verification_code, name='send_verification_code'),
    path('code/verify/', verify_code, name='verify_code'),
    path('code/reset_password/', send_password_reset_code,
         name='send_password_reset_code'),
    path('code/verify_password_reset/', verify_password_reset_code,
         name='verify_password_reset_code'),

    # Point URLs
    path('points/create/', create_point, name='create_point'),
    path('points/<int:point_id>/', get_point_info, name='get_point_info'),
    path('points/', get_all_points, name='get_all_points'),
    path('points/<int:point_id>/status/',
         change_point_status, name='change_point_status'),
    path('points/<int:point_id>/delete/',
         name='delete_point', view=delete_point),
    path('points/me/<int:point_id>/delete/',
         delete_my_point, name='delete_my_point'),
    path('points/<int:point_id>/add_view/',
         add_view, name='add_view'),
    path('points/<int:point_id>/edit/', edit_point, name='edit_point'),
    path('points/map/', show_points_on_map, name='show_points_on_map'),
    path('points/<int:point_id>/approve/',
         point_approval, name='point_approval'),
    # Terms and Conditions URLs
    path('terms/create/', create_terms, name='create_terms'),
    path('terms/<int:term_id>/', get_terms, name='get_terms'),
    path('terms/<int:term_id>/update/', update_terms, name='update_terms'),

    # Review URLs
    path('points/<int:point_id>/review/',
         add_review, name='add_review'),

    # Photo management URLs
    path('users/<int:user_id>/photo/upload/',
         create_photo, name='user-photo-upload'),
    path('points/<int:point_id>/photo/upload/',
         create_photo, name='point-photo-upload'),
    path('users/<int:user_id>/photo/update/<int:photo_id>/',
         update_photo, name='user-photo-update'),
    path('points/<int:point_id>/photo/update/<int:photo_id>/',
         update_photo, name='point-photo-update'),
    path('photos/', get_photo, name='photo-list'),
    path('photos/delete/', delete_photo, name='photo-delete'),
]
