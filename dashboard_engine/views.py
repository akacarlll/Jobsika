import json

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
                "timeline": dashboards["timeline_dashboards"],
                "stats": {
                    "total": len(dashboards_creator.job_application_df),
                    "cities": dashboards_creator.job_application_df[
                        "Location"
                    ].nunique(),
                    "week": dashboards["date_stats"]["current_week"],
                },
                "date_stats": dashboards["date_stats"]
            }
        }

        return render(request, "dashboard_engine/dashboard_page.html", context)
