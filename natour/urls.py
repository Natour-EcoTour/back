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

from .api.views.auth import MyTokenObtainPairView, create_user, login
from .api.views.users import get_my_info, delete_my_account, update_my_info
from .api.views.photo import create_photo, update_photo, get_photo, delete_photo

urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),

    # Auth URLs
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User management URLs
    path('users/login/', login, name='login'),
    path('users/create/', create_user, name='create_user'),
    path('users/me/', get_my_info, name='get_my_info'),
    path('users/me/update/', update_my_info, name='update_my_info'),
    path('users/me/delete/', delete_my_account, name='delete_my_account'),

    # Photo management URLs
    path('users/<int:user_id>/photo/upload/', create_photo, name='user-photo-upload'),
    path('points/<int:point_id>/photo/upload/', create_photo, name='point-photo-upload'),
    path('users/<int:user_id>/photo/update/<int:photo_id>/', \
         update_photo, name='user-photo-update'),
    path('points/<int:point_id>/photo/update/<int:photo_id>/', \
         update_photo, name='point-photo-update'),

    path('photos/', get_photo, name='photo-list'),
    path('photos/delete/', delete_photo, name='photo-delete'),
]
