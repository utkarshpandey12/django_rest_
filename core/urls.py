from django.urls import path

from . import views

app_name = "core"
urlpatterns = [
    path("", view=views.RootView.as_view(), name="root_view"),
    path("otp/send", view=views.SendOtp.as_view(), name="send_otp_view"),
    path("otp/verify", view=views.VerifyOtp.as_view(), name="verify_otp_view"),
    path("mpin/set", view=views.SetMpin.as_view(), name="set_mpin_view"),
    path("mpin/verify", view=views.VerifyMpin.as_view(), name="verify_mpin_view"),
    path("token/refresh", view=views.RefreshToken.as_view(), name="refresh_token_view"),
    path(
        "referral/verify",
        view=views.VerifyReferralCode.as_view(),
        name="referral_code_view",
    ),
    path(
        "profession/update",
        views.MbxUserUpdateView.as_view(),
        name="mbx_user_profession_update",
    ),
]
