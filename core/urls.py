from django.urls import path

from . import views

app_name = "core"
urlpatterns = [
    path("", view=views.RootView.as_view(), name="root_view"),
]
