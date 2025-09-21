from django.urls import path
from .views import HomeView, GoogleAuthCallbackView

app_name = "home_page"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),  # Main page
    path("home-page/", HomeView.as_view(), name="home_page_form"),  # Alternative route
    path("auth/google/callback/", GoogleAuthCallbackView.as_view(), name="google_callback"),
]



