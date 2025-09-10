from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path, include

from general import plain_redirect, get_default_context
from . import views

error_urls = [path("", lambda *args: plain_redirect("/")),
              path("<int:status_code>", views.error_page), ]

account_urls = [path("login",
                     LoginView.as_view(
                         template_name="special/login.html",
                         extra_context={**get_default_context(None), "suppress_navbar": True}, ), name="login")]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(account_urls)),
    path("dev/", include("dev.urls")),
    path("", include("root.urls")),
    path("error/", include(error_urls)),
    path("favicon.ico", lambda *args: plain_redirect("/images/site/icon.png", True))
]
