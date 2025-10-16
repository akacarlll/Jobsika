"""This is the main entry for the jobs_engine app that add data from a job description to a sheet."""

import logging
import time

import requests
from django.conf import settings
from django.contrib import messages
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.views import View

from .google_sheet_manager import GoogleSheetsManager
from .job_application_processor import JobApplicationProcessor

logger = logging.getLogger(__name__)


class JobPostingView(View):
    """View for handling job posting submissions and processing job offers."""

    def post(self, request: HttpRequest):

        access_token: str = request.session.get("google_access_token", "")
        if not access_token:
            messages.error(request, "❌ Please log in with Google first.")
            return redirect("home_page:home")

        token_expires_at = request.session.get("google_token_expires_at", 0)
        if time.time() >= token_expires_at:
            if not self.refresh_access_token(request):
                messages.error(request, "❌ Your session expired. Please log in again.")
                return redirect("home_page:home")
            access_token: str = request.session.get("google_access_token", "")
        job_url = request.POST.get("job_url", "").strip()
        job_url_description = request.POST.get("job_url_for_description", "").strip()
        job_description = request.POST.get("job_description", "").strip()
        notes = request.POST.get("notes", "")

        if not job_url and not job_description:
            messages.error(
                request, "❌ Please provide either a job URL or job description."
            )
            return redirect("jobs_engine:add_job")

        application_processor = JobApplicationProcessor(notes=notes)

        try:
            if job_url:
                application_processor.url = job_url
                data = application_processor.process_job_offer()
            else:
                application_processor.url = job_url_description
                data = application_processor.process_job_offer(
                    job_description=job_description
                )
        except Exception as e:
            logger.error(f"Error processing job offer: {e}", exc_info=True)
            messages.error(
                request, "❌ Failed to process the job offer. Please try again."
            )
            return redirect("jobs_engine:add_job")

        logger.info("Successfully processed job offer.")

        try:
            sheets_manager = GoogleSheetsManager(access_token)

            spreadsheet_id = sheets_manager.get_or_create_spreadsheet()

            sheets_manager.append_row(spreadsheet_id, data)

            messages.success(request, f"✅ {data['job_title']} was successfully added!")
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                messages.error(
                    request, "❌ Authentication expired. Please log in again."
                )
                return redirect("home_page:home")
            logger.error(f"HTTP error sending to Google Sheets: {e}", exc_info=True)
            messages.error(
                request, "❌ Failed to save to Google Sheets. Please try again."
            )
        except requests.RequestException as e:
            logger.error(f"Error sending to Google Sheets: {e}", exc_info=True)
            messages.error(
                request, "❌ Failed to connect to Google Sheets. Please try again."
            )

        return redirect("jobs_engine:add_job")

    def get(self, request: HttpRequest):
        """
        Handles GET requests to render the add job form page.

        Args:
            request (HttpRequest): The HTTP request object.

        Returns:
            HttpResponse: Renders the add job form template.
        """

        return render(request, "jobs_engine/add_job.html")

    def refresh_access_token(self, request: HttpRequest) -> bool:
        """
        Refreshes the access token using the refresh token.

        Args:
            request: The HTTP request object

        Returns:
            True if refresh was successful, False otherwise
        """
        refresh_token = request.session.get("google_refresh_token")
        if not refresh_token:
            return False

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token",
        }

        try:
            response = requests.post(token_url, data=data, timeout=10)
            response.raise_for_status()
            token_data = response.json()

            access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)

            if not access_token:
                return False

            request.session["google_access_token"] = access_token
            request.session["google_token_expires_at"] = time.time() + expires_in

            logger.info("Successfully refreshed access token")
            return True

        except requests.RequestException as e:
            logger.error(f"Error refreshing access token: {e}", exc_info=True)
            return False


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
