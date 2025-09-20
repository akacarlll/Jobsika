from django.urls import path
from .views import JobFormView, GoogleAuthCallbackView, DisconnectView, JobPostingView

app_name = "jobs_engine"

# urlpatterns = [
#     path("add-job/", JobFormView.as_view(), name="add_job"),
#     path(
#         "auth/google/callback/",
#         GoogleAuthCallbackView.as_view(),
#         name="google_callback",
#     ),
# ]
urlpatterns = [
    path("", JobFormView.as_view(), name="home"),  # URL racine
    path("add-job/", JobFormView.as_view(), name="add_job"),
    path(
        "auth/google/callback/",
        GoogleAuthCallbackView.as_view(),
        name="google_callback",
    ),
    path("process-job/", JobPostingView.as_view(), name="process_job"),
    path("disconnect/", DisconnectView.as_view(), name="disconnect"),
]
