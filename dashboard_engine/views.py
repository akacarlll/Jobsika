
import requests
from django.conf import settings
from django.shortcuts import render
from django.views import View

from .create_dashboard import DashboardCreator


class DashboardView(View):
    """View for rendering the dashboard page with job application statistics and map."""

    def get(self, request):
        """
        Handles GET requests to display the dashboard page.
        Fetches job application data, creates dashboards, and renders the dashboard template.
        """
        response = requests.get(settings.SHEETS_SCRIPT_URL)
        dashboards_creator = DashboardCreator(response.json())
        dashboards = dashboards_creator.create_all_dashboards()

        context = {
            "dashboards": {
                "map": dashboards["map"],
                "skills_pie": dashboards["skills_pie"],
                "timeline_dashboards": dashboards["timeline_dashboards"],
                "date_stats": dashboards["general_stats"]
            }
        }

        return render(request, "dashboard_engine/dashboard_page.html", context)
