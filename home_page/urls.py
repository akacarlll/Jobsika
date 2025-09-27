from django.urls import path

from .views import GoogleAuthCallbackView, HomeView

app_name = "home_page"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("home-page/", HomeView.as_view(), name="home_page_form"),
    path("auth/google/callback/", GoogleAuthCallbackView.as_view(), name="google_callback"),
]



