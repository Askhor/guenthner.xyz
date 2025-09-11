from django.http import HttpResponsePermanentRedirect
from django.urls import path, include

from . import views

app_name = "private"

ffs_urls = [path("", views.view_index, name="ffs"),
            path("<str:api>/", views.view_api, name="api"),
            path("<str:api>/<path:path>", views.view_api, name="api"), ]

urlpatterns = [path("ffs/", include(ffs_urls)),
               path("", lambda *a: HttpResponsePermanentRedirect("ffs/")), ]
