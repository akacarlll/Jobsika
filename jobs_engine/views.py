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
        print(sheet_response)
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
            "url": self.data["url"],
            "title": self.data["job_title"],
        }
        resp = requests.post(script_url, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()


class JobFormView(View):
    def get(self, request):

        state_token = secrets.token_urlsafe(32)
        request.session["google_oauth_state"] = state_token
        google_auth_params = {
            "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "scope": " ".join(settings.GOOGLE_SHEETS_SCOPES),
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "state": state_token,
        }

        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/auth?{urlencode(google_auth_params)}"
        )

        context = {
            "google_auth_url": google_auth_url,
        }

        return render(request, "jobs_engine/add_job.html", context)


class GoogleAuthCallbackView(View):
    def get(self, request):

        code = request.GET.get("code")
        state = request.GET.get("state")

        session_state = request.session.get("google_oauth_state")
        if not state or state != session_state:
            return JsonResponse({"error": "Invalid state token"}, status=400)

        if code:
            # TODO: Treat the authorization code, for now, we just confirming connexion
            request.session["google_authenticated"] = True
            return render(request, "jobs_engine/auth_success.html", {"code": code})
        else:
            error = request.GET.get("error", "Unknown error")
            return render(request, "jobs_engine/auth_error.html", {"error": error})


class DisconnectView(View):
    def post(self, request):
        request.session.pop("google_authenticated", None)
        request.session.pop("google_auth_code", None)
        request.session.pop("google_oauth_state", None)

        return JsonResponse({"status": "disconnected"})
