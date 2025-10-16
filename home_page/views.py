import secrets
from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
import requests

class HomeView(View):
    """View for rendering the home page and initiating Google OAuth2 authentication."""

    def get(self, request: HttpRequest):
        """
        Handles GET requests to the home page.
        Generates a state token, constructs the Google OAuth2 URL, and renders the authentication page.

        Args:
            request (HttpRequest): The HTTP request object.
        """
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
    """View to handle the callback from Google OAuth2 authentication."""

    def get(self, request):
        """
        Handles GET requests from Google's OAuth2 callback.
        Validates the state token and processes the authentication code.
        Redirects to the add_job page on success, or renders an error page on failure.

        Args:
            request (HttpRequest): The HTTP request object.
        """
        code = request.GET.get("code")
        state = request.GET.get("state")
        session_state = request.session.get("google_oauth_state")

        if not state or state != session_state:
            return JsonResponse({"error": "Invalid state token"}, status=400)

        if not code:
            error = request.GET.get("error", "Unknown error")
            return render(request, "home_page/auth_error.html", {"error": error})

        token_url = "https://oauth2.googleapis.com/token"
        data = {
            "code": code,
            "client_id": settings.GOOGLE_OAUTH2_CLIENT_ID,
            "client_secret": settings.GOOGLE_OAUTH2_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }

        response = requests.post(token_url, data=data)
        token_data = response.json()

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token")

        if "access_token" not in token_data:
            return JsonResponse({"error": "Failed to retrieve access token", "details": token_data}, status=400)

        request.session["google_access_token"] = access_token
        request.session["google_refresh_token"] = refresh_token

        return redirect(reverse("jobs_engine:add_job"))

class CheckAuthView(View):
    """View to check if the current user is authenticated."""

    def get(self, request):
        """
        Handles GET requests to check user authentication status.
        Returns a JSON response indicating whether the user is authenticated.

        Args:
            request (HttpRequest): The HTTP request object.
        """
        if "google_access_token" in request.session:
            return JsonResponse({"authenticated": True})
        return JsonResponse({"authenticated": False}, status=401)
