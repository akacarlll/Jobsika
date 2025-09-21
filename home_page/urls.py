from django.urls import path
from .views import JobFormView, GoogleAuthCallbackView, CheckAuthView

app_name = "home_page"

urlpatterns = [
    path("", JobFormView.as_view(), name="home"),  # Main page
    path("home-page/", JobFormView.as_view(), name="home_page_form"),  # Alternative route
    path("auth/google/callback/", GoogleAuthCallbackView.as_view(), name="google_callback"),
    path("check-auth/", CheckAuthView.as_view(), name="check_auth"),
]



