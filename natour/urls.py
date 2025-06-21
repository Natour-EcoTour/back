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
from .api.views.users import get_my_info
from .api.views.photo import create_photo

urlpatterns = [
    path('admin/', admin.site.urls),

    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('users/create/', create_user, name='create_user'),
    path('users/login/', login, name='login'),

    path('users/me/', get_my_info, name='get_my_info'),

    path('photos/upload/', create_photo, name='photo-upload')
]
