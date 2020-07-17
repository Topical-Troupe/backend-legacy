"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
	https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
<<<<<<< HEAD
from django.urls import include, path

from .rest import router, UserViewSet

urlpatterns = [
	path('admin/', admin.site.urls),

	path('api/', include(router.urls)),
	path('api/me/', UserViewSet.as_view({ 'get': 'me' }), name = 'me')
=======
from django.urls import path
from django.conf import settings
from django.conf.urls import url, include
from rest_framework import routers, serializers, viewsets


"""
The 'path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))' may not be necessary since we are using djoser
"""

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.authtoken')),

>>>>>>> refs/remotes/origin/main
]