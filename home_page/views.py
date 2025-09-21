from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render, redirect
import requests
from django.conf import settings
from urllib.parse import urlencode
import secrets
import logging

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
        return render(request, "home_page/auth.html", context)


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
            return render(request, "home_page/auth_success.html", {"code": code})
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