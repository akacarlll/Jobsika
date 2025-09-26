import logging

import requests
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.views import View

from .service import JobApplicationProcessor

logger = logging.getLogger(__name__)


class JobPostingView(View):
    """
    View for handling job posting submissions and processing job offers.
    Handles both GET and POST requests for adding job offers and sending them to Google Sheets.
    """

    def post(self, request: HttpRequest):
        """
        Handles POST requests to process a job offer from a URL or description,
        sends the processed data to Google Sheets, and provides user feedback.

        Args:
            request (HttpRequest): The HTTP request object containing form data.

        Returns:
            HttpResponseRedirect: Redirects to the add job form page with a success or error message.
        """
        job_url = request.POST.get("job_url", "")
        if not job_url:
            job_url = request.POST.get("job_url_for_description", "")
        job_description = request.POST.get("job_description")
        notes = request.POST.get("notes", "")
        application_processor = JobApplicationProcessor(notes=notes)

        # TODO: Verify thats it's a requetable URL

        if job_url:
            application_processor.url = job_url
            self.data = application_processor.process_job_offer()
        if job_description:
            application_processor.url = job_url
            self.data = application_processor.process_job_offer(
                job_description=job_description
            )

        logger.info("Successfully processed the URL.")

        sheet_response = self.send_to_sheet()
        if sheet_response == 200:
            messages.success(
                request,
                f"✅ {self.data['job_title']} was successfully added to the sheets!",
            )
        else:
            messages.error(
                request, f"{self.data['job_title']} was not added to the sheets!"
            )
        return redirect("jobs_engine:add_job")

    def send_to_sheet(self) -> int:
        """
        Sends the processed job data to the Google Sheets script endpoint.

        Returns:
            int: The HTTP status code from the Sheets script response.
        """
        script_url = settings.SHEETS_SCRIPT_URL
        payload = {
            **self.data,
        }
        resp = requests.post(script_url, json=payload, timeout=10)
        resp.raise_for_status()

        logger.info(f"Response status code: {resp.status_code}")

        return resp.status_code

    def get(self, request: HttpRequest):
        """
        Handles GET requests to render the add job form page.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: Renders the add job form template.
        """

        return render(request, "jobs_engine/add_job.html")


class DisconnectView(View):
    """
    View for handling user disconnection from Google authentication.
    Removes authentication-related session data and redirects to the home page.
    """

    def get(self, request):
        """
        Handles GET requests to disconnect the user from Google authentication.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponseRedirect: Redirects to the home page.
        """
        request.session.pop("google_authenticated", None)
        request.session.pop("google_auth_code", None)
        request.session.pop("google_oauth_state", None)

        return redirect("home_page:home")
