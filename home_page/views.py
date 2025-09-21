from django.views import View
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.conf import settings
from urllib.parse import urlencode
import secrets
from django.urls import reverse

class HomeView(View):
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
        return render(request, "home_page/auth.html", context)

class GoogleAuthCallbackView(View):
    def get(self, request):
        code = request.GET.get("code")
        state = request.GET.get("state")
        session_state = request.session.get("google_oauth_state")

        if not state or state != session_state:
            return JsonResponse({"error": "Invalid state token"}, status=400)

        if code:
            request.session["google_authenticated"] = True

            return redirect(reverse("jobs_engine:add_job"))  # or dashboard
        else:
            error = request.GET.get("error", "Unknown error")
            return render(request, "home_page/auth_error.html", {"error": error})

class CheckAuthView(View):
    """  """
    def get(self, request):
        print(request)
        if request.user.is_authenticated:
            return JsonResponse({"authenticated": True})
        return JsonResponse({"authenticated": False}, status=401)
