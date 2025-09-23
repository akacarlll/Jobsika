from django.shortcuts import render
import requests

from django.conf import settings
from .create_dashboard import DashboardCreator
from django.views import View
import json 
from plotly.utils import PlotlyJSONEncoder

class DashboardView(View):

    def get(self, request):
        response = requests.get(settings.SHEETS_SCRIPT_URL)
        dashboards_creator = DashboardCreator(response.json())
        map_figures = dashboards_creator.create_all_dashboards()
        
        context = {
            "map_figures": {
                "map": json.dumps(map_figures),
                "stats": {
                    "total": len(dashboards_creator.job_application_df),
                    "cities": dashboards_creator.job_application_df["Location"].nunique(),
                    "week": 0
                }
            }
        }
        
        return render(request, "dashboard_engine/dashboard_page.html", context)
