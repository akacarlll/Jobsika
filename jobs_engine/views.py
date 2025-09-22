from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .service import JobApplicationProcessor
import requests
from django.conf import settings
import logging
from django.contrib import messages
from django.shortcuts import render, redirect

logger = logging.getLogger(__name__)


@method_decorator(
    csrf_exempt, name="dispatch"
)
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
        if sheet_response == 200:
            messages.success(
                request,
                f"✅ {self.data['job_title']} was successfully added to the sheets!"
            )
        else:
            messages.error(request,
                f"{self.data['job_title']} was not added to the sheets!"
            )
        # Redirect back to the form page
        return redirect('jobs_engine:add_job')

    def send_to_sheet(self)-> int:
        """_summary_

        Returns:
            int: _description_
        """
        script_url = settings.SHEETS_SCRIPT_URL
        payload = {
            **self.data,
        }
        resp = requests.post(script_url, json=payload, timeout=10)
        resp.raise_for_status()

        logger.info(f"Response status code: {resp.status_code}")

        return resp.status_code

    def get(self, request):

        return render(request, "jobs_engine/add_job.html")





class DisconnectView(View):
    """_summary_

    Args:
        View (_type_): _description_
    """

    def get(self, request):
        print("get request received")
        request.session.pop("google_authenticated", None)
        request.session.pop("google_auth_code", None)
        request.session.pop("google_oauth_state", None)

        return redirect('home_page:home')


