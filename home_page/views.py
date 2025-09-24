import secrets
from urllib.parse import urlencode

from django.conf import settings
from django.http import HttpRequest, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View


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

        if code:
            request.session["google_authenticated"] = True

            return redirect(reverse("jobs_engine:add_job"))  # or dashboard
        else:
            error = request.GET.get("error", "Unknown error")
            return render(request, "home_page/auth_error.html", {"error": error})


class CheckAuthView(View):
    """View to check if the current user is authenticated."""

    def get(self, request):
        """
        Handles GET requests to check user authentication status.
        Returns a JSON response indicating whether the user is authenticated.

        Args:
            request (HttpRequest): The HTTP request object.
        """
        if request.user.is_authenticated:
            return JsonResponse({"authenticated": True})
        return JsonResponse({"authenticated": False}, status=401)
