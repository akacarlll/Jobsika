from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .service import JobApplicationProcessor
from .models import JobPosting
import requests
from django.conf import settings
from urllib.parse import urlencode
import secrets
import logging
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)


@method_decorator(
    csrf_exempt, name="dispatch"
)  # remove if using CSRF tokens in frontend
class JobPostingView(View):

    def post(self, request, *args, **kwargs):
        job_url = request.POST.get("job_url", "")
        job_description = request.POST.get('job_description')
        notes = request.POST.get("notes", "")
        application_processor = JobApplicationProcessor(notes=notes)

        # TODO: Verify thats it's a requetable URL

        if job_url:
            application_processor.url = job_url
            self.data = application_processor.process_job_offer()
        if job_description:
            self.data = application_processor.process_job_offer(job_description=job_description)

        logger.info("Successfully processed the URL.")
        
        sheet_response = self.send_to_sheet()

        return JsonResponse(
            {
                "processed_data": self.data,
                "sheet_response": sheet_response,
            }
        )

    def send_to_sheet(self):
        script_url = settings.SHEETS_SCRIPT_URL
        payload = {
            **self.data,
        }
        resp = requests.post(script_url, json=payload, timeout=10)
        resp.raise_for_status()
        
        logger.info(f"Response status code: {resp.status_code}")
        return resp.json()
    def get(self, request):

        return render(request, "jobs_engine/add_job.html")





class DisconnectView(View):
    """_summary_

    Args:
        View (_type_): _description_
    """
    def post(self, request):
        request.session.pop("google_authenticated", None)
        request.session.pop("google_auth_code", None)
        request.session.pop("google_oauth_state", None)

        return JsonResponse({"status": "disconnected"})

