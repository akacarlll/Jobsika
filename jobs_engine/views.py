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
        url = request.POST["job_url"]
        notes = request.POST.get("notes", "")

        # TODO: Verify thats it's a requetable URL

        application_processor = JobApplicationProcessor(url)
        self.data = application_processor.process_job_offer()

        logger.info("Successfully processed the URL.")

        sheet_response = self.send_to_sheet()

        return JsonResponse(
            {
                "url": url,
                "notes": notes,
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

