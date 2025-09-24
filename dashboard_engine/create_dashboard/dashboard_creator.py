import json

import pandas as pd
import plotly
import plotly.express as px


class DashboardCreator:
    """Class for creating dashboards from job application data."""

    def __init__(self, job_application_data: list[dict]):
        """
        Initialize DashboardCreator with job application data.

        Args:
            job_application_data (list[dict]): List of job application records.
        """
        self.job_application_df = pd.DataFrame(job_application_data)

    def create_map_dashboard(self):
        """
        Create a map dashboard visualizing job applications by city location.

        Returns:
            str: JSON-encoded Plotly figure.
        """
        french_city_location = pd.read_csv("data/french_city_location.csv")

        latitudes = []
        longitudes = []
        for city in self.job_application_df["Location"].values:
            if city in french_city_location["city"].values:
                latitudes.append(
                    french_city_location.loc[
                        french_city_location["city"] == city, "lat"
                    ].values[0]
                )
                longitudes.append(
                    french_city_location.loc[
                        french_city_location["city"] == city, "lng"
                    ].values[0]
                )
            else:
                latitudes.append(None)
                longitudes.append(None)

        df = pd.DataFrame(
            {
                "city": self.job_application_df["Location"].values,
                "lat": latitudes,
                "lon": longitudes,
            }
        )

        df_grouped = df.groupby(["city", "lat", "lon"], as_index=False).size()
        df_grouped.rename(columns={"size": "count"}, inplace=True)

        fig = px.scatter_mapbox(
            df_grouped,
            lat="lat",
            lon="lon",
            hover_name="city",
            size="count",
            color="count",
            zoom=4,
            height=500,
            color_continuous_scale=px.colors.cyclical.IceFire,
        )

        fig.update_layout(mapbox_style="open-street-map")

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    # def create

    def create_all_dashboards(self) -> dict:
        """
        Create all dashboards and return them as a dictionary.

        Returns:
            dict: Dictionary containing all generated dashboards.
        """
        return {"map": self.create_map_dashboard()}
