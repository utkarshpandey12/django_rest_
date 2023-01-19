from django.urls import path

from . import views

app_name = "core"
urlpatterns = [
    path("otp/send", view=views.SendOtp.as_view(), name="send_otp_view"),
    path("otp/verify", view=views.VerifyOtp.as_view(), name="verify_otp_view"),
]
