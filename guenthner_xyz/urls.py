"""
URL configuration for guenthner_xyz project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path, include

from general import plain_redirect
from . import views

app_name = "guenthner_xyz"
urlpatterns = [
    # path("admin/", admin.site.urls),
    path("", include("root.urls")),
    path("404", views.error_page),
    path("favicon.ico", lambda: plain_redirect("/images/site/icon.png", True))
]
