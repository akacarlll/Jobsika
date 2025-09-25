from django.urls import path

from .views import DisconnectView, JobPostingView


app_name = "jobs_engine"

urlpatterns = [
    path("add-job/", JobPostingView.as_view(), name="add_job"),
    path("process-job/", JobPostingView.as_view(), name="process_job"),
    path("disconnect/", DisconnectView.as_view(), name="disconnect"),
]
