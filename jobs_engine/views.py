from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .service import JobApplicationProcessor
from .models import JobPosting
from django.conf import settings
from urllib.parse import urlencode
import secrets

@method_decorator(csrf_exempt, name="dispatch")  # remove if using CSRF tokens in frontend
class JobPostingView(View):

    def post(self, request, *args, **kwargs):
        url = request.POST.get("url")

        # TODO: Verify thats it's a requetable URL

        application_processor = JobApplicationProcessor(url)
        data = application_processor.process_job_offer()
        print("Application processed.\n\n")


        # Save to DB
        job = JobPosting.objects.create(
            job_title=data.get("title", "Untitled"),
            company_name=data.get("company", "Unknown"),
            url=url,
            job_description_summary=data.get("description", ""),
        )

        return JsonResponse(
            {
                "status": "ok",
                "title": job.job_title,
                "company": job.company_name,
            },
            status=201,
        )

class JobFormView(View):
    def get(self, request):

        state_token = secrets.token_urlsafe(32)
        request.session['google_oauth_state'] = state_token
        
        # Paramètres pour la popup Google OAuth
        google_auth_params = {
            'client_id': settings.GOOGLE_OAUTH2_CLIENT_ID,
            'redirect_uri': settings.GOOGLE_REDIRECT_URI,
            'scope': ' '.join(settings.GOOGLE_SHEETS_SCOPES),
            'response_type': 'code',
            'access_type': 'offline',
            'prompt': 'consent',
            'state': state_token
        }
        
        google_auth_url = f"https://accounts.google.com/o/oauth2/auth?{urlencode(google_auth_params)}"

        context = {
            'google_auth_url': google_auth_url,
        }
        
        return render(request, "jobs_engine/add_job.html", context)
    
class GoogleAuthCallbackView(View):
    def get(self, request):

        print("Google Auth Callback")
        # Cette vue gérera la réponse de Google après l'authentification
        code = request.GET.get('code')
        state = request.GET.get('state')
        
        # Vérifier le state token pour la sécurité
        session_state = request.session.get('google_oauth_state')
        if not state or state != session_state:
            return JsonResponse({'error': 'Invalid state token'}, status=400)
        
        if code:
            # Ici vous traiterez le code d'autorisation
            # Pour l'instant, on confirme juste la connexion
            request.session['google_authenticated'] = True
            return render(request, 'jobs_engine/auth_success.html', {'code': code})
        else:
            error = request.GET.get('error', 'Unknown error')
            return render(request, 'jobs_engine/auth_error.html', {'error': error})
class DisconnectView(View):
    def post(self, request):
        # Supprimer les données d'authentification de la session
        request.session.pop('google_authenticated', None)
        request.session.pop('google_auth_code', None)
        request.session.pop('google_oauth_state', None)
        
        return JsonResponse({'status': 'disconnected'})