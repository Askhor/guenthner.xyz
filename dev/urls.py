from django.urls import path

from . import views

app_name = "dev"
urlpatterns = [
    path("", views.view_index, name="index"),
    path("log/<slug:service>/<slug:name>", views.view_log, name="log"),
]
