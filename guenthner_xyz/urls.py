from django.contrib import admin
from django.urls import path, include

from general import plain_redirect
from . import views

error_urls = [path("", lambda *args: plain_redirect("/")),
              path("<int:status_code>", views.error_page), ]

urlpatterns = [
    path("dev/admin/", admin.site.urls),
    path("dev/", include("dev.urls")),
    path("", include("root.urls")),
    path("error/", include(error_urls)),
    path("favicon.ico", lambda *args: plain_redirect("/images/site/icon.png", True))
]
