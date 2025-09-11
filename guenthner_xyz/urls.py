from django.conf import settings
from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path, include

from general import plain_redirect, get_default_context, MySitemap
from . import views

error_urls = [path("", lambda *args: plain_redirect("/")),
              path("<int:status_code>", views.error_page), ]

account_urls = [path("login",
                     LoginView.as_view(
                         template_name="special/login.html",
                         extra_context={**get_default_context(None), "suppress_navbar": True}, ), name="login")]

indexed_routes = "index,math,eratosthenes,mandelbrot,paper,pretty,memes,words,pictures,creations,chat,cowsay".split(",")

debug_static_routes = []

if settings.DEBUG:
    debug_static_routes = [path("js/<path:path>", views.view_debug_static("text/js")),
                           path("css/<path:path>", views.view_debug_static("text/css")), ]

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(account_urls)),
    path("", include(debug_static_routes)),
    path("dev/", include("dev.urls")),
    path("private/", include("private.urls")),
    path("", include("root.urls")),
    path("error/", include(error_urls)),
    path("favicon.ico", lambda *args: plain_redirect("/images/site/icon.png", True)),
    MySitemap.with_path("sitemap.xml",
                        *[f"root:{i}" for i in indexed_routes]),

]
