import json
from urllib.parse import urlparse

import pandas as pd
import plotly
import plotly.express as px
from django.conf import settings


class DashboardCreator:
    """Class for creating dashboards from job application data."""

    def __init__(self, job_application_data: list[dict]):
        """
        Initialize DashboardCreator with job application data.

        Args:
            job_application_data (list[dict]): List of job application records.
        """
        self.job_application_df = pd.DataFrame(job_application_data)

    def clean_location(self, df, column='Location'):
        """Remove unwanted text patterns from location column."""
        patterns = [
            r'\s*-\s*\d+',  # Postal codes
            r'\(67\)',
            r'et périphérie',
            r'\(hybride\)',
            r'\(relocation from levallois-perret planned from april 2025\)',
            r' \(occasional remote work\)',
            r"ville de"
        ]

        result = df[column].copy()
        for pattern in patterns:
            result = result.str.lower().replace(pattern, '', regex=True)
        return result.str.strip()

    def read_city_location_csv(self, country_code: str) -> pd.DataFrame:
        """Read city location data from a CSV file.

        Args:
            country_code (str): The country code (e.g., "fr", "us"...).

        Returns:
            pd.DataFrame: City location data.
        """
        return pd.read_csv(f"data/{country_code.lower()}_city_location.csv")

    def load_and_merge_city_data(self) -> pd.DataFrame:
        """
        Load and merge city location data from CSV files.

        Returns:
            pd.DataFrame: Merged city location data.
        """
        city_location_dfs = list(map(self.read_city_location_csv, settings.COUNTRY_APPLIED))
        return pd.concat(city_location_dfs, ignore_index=True)

    def create_map_dashboard(self) -> str:
        """
        Create a map dashboard visualizing job applications by city location.

        Returns:
            str: JSON-encoded Plotly figure.
        """
        city_locations = self.load_and_merge_city_data()

        self.job_application_df["Location"] = self.clean_location(self.job_application_df)

        locations_data = []

        for city in self.job_application_df["Location"].values:
            if pd.isna(city):
                continue

            city_stripped = str(city).strip().lower()
            city_clean = city_stripped.split(",")[0].strip()
            city_match = city_locations[city_locations["city"] == city_clean]


            if not city_match.empty:
                locations_data.append({
                    "city": city_stripped,
                    "city_clean": city_clean,
                    "lat": float(city_match.iloc[0]["lat"]),
                    "lng": float(city_match.iloc[0]["lng"])
                })

        self.locations_found_df = pd.DataFrame(locations_data)

        df_grouped = self.locations_found_df.groupby(["city_clean", "lat", "lng"], as_index=False).size()
        df_grouped.rename(columns={"size": "count"}, inplace=True)

        df_grouped = df_grouped.dropna(subset=['lat', 'lng'])

        px.set_mapbox_access_token(settings.MAPBOX_TOKEN)

        fig = px.scatter_map(
            df_grouped,
            lat="lat",
            lon="lng",
            hover_name="city_clean",
            size="count",
            color="count",
            zoom=6,
            height=500,
            color_continuous_scale="Viridis",
            size_max=15,
        )

        fig.update_layout(
            mapbox_style="open-street-map",
            mapbox={
                "center": {"lat": 48.8566, "lon": 2.3522},
                "zoom": 6
            },
            margin={"r": 0, "t": 30, "l": 0, "b": 0},
            showlegend=False
        )

        fig.update_traces(
            marker={
                "sizemin": 10,
                "opacity": 0.8,
            }
        )

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)



    def plot_skills_pie(self, col: str ="Skills Required", top_n: int = 20) -> str:
        """
        Create a pie chart visualization of the most requested skills.

        Args:
            col (str): Column name containing the skills.
            top_n (int): The number of skills to display.

        Returns:
            str: JSON-encoded Plotly figure.
        """
        skills_series = self.job_application_df[col].dropna().apply(lambda x:
            [s.strip().lower() for s in x.split(",") if s.strip()])
        all_skills = [skill for sublist in skills_series for skill in sublist if skill]

        skill_counts = pd.Series(all_skills).value_counts().reset_index()
        skill_counts.columns = ["Skill", "Count"]
        if len(skill_counts) > top_n:
            top_skills = skill_counts[:top_n]
            autres = pd.Series({"Autres": skill_counts[top_n:].sum()})
            skill_counts = pd.concat([top_skills, autres])

        fig = px.pie(
            skill_counts,
            names="Skill",
            values="Count",
            hole=0.2
        )

        fig.update_traces(textposition="inside", textinfo="percent+label")
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def plot_url_pie(self, col: str = "URL", top_n: int = 10) -> str:
        """
        Create a pie chart visualization of the most frequent application websites.

        Args:
            col (str): Column name containing the URLs.
            top_n (int): The number of domains to display.

        Returns:
            str: JSON-encoded Plotly figure.
        """
        df = self.job_application_df.copy()
        df = df.dropna(subset=[col])

        df["domain"] = df[col].apply(
            lambda x: urlparse(x).netloc.replace("www.", "").strip().lower()
            if pd.notnull(x) else None
        )
        df["domain"] = df["domain"].replace("", "Non Précisé")
        print(df["domain"].value_counts())

        domain_counts = df["domain"].value_counts().reset_index()
        domain_counts.columns = ["Domain", "Count"]

        if len(domain_counts) > top_n:
            top_domains = domain_counts[:top_n]
            autres = pd.DataFrame([{
                "Domain": "Autres",
                "Count": domain_counts["Count"][top_n:].sum()
            }])
            domain_counts = pd.concat([top_domains, autres], ignore_index=True)

        fig = px.pie(
            domain_counts,
            names="Domain",
            values="Count",
            hole=0.2,
            title="Répartition des candidatures par site web"
        )

        fig.update_traces(textposition="inside", textinfo="percent+label")

        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    def create_comprehensive_timeline_dashboard(self, date_applied_col: str = "Date Applied") -> dict:
        """Create multiple date-based visualizations."""
        df = self.job_application_df.copy()
        df[date_applied_col] = pd.to_datetime(df[date_applied_col])

        current_week = df[df[date_applied_col] >= df[date_applied_col].max() - pd.Timedelta(days=6)]

        daily_apps = df.groupby(df[date_applied_col].dt.date).size().reset_index()
        daily_apps.columns = ['Date', 'Applications']

        timeline_fig = px.line(
            daily_apps,
            x='Date',
            y='Applications',
            markers=True
        )
        timeline_fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Candidatures",
            showlegend=False
        )

        current_week['Hour'] = current_week[date_applied_col].dt.hour
        hourly_dist = current_week['Hour'].value_counts().sort_index().reset_index()
        hourly_dist.columns = ['Heure', 'Candidatures']

        hourly_fig = px.bar(
            hourly_dist,
            x='Heure',
            y='Candidatures',
        )
        hourly_fig.update_layout(
            xaxis_title="Heure",
            yaxis_title="Nombre de candidatures",
            showlegend=False
        )

        current_week['DayOfWeek'] = current_week[date_applied_col].dt.day_name()
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']

        daily_dist = current_week['DayOfWeek'].value_counts().reindex(day_order).reset_index()
        daily_dist.columns = ['Day', 'Candidatures']
        daily_dist['Jour'] = day_fr

        daily_fig = px.bar(
            daily_dist,
            x='Jour',
            y='Candidatures',
        )

        df['Month'] = df[date_applied_col].dt.to_period('M').dt.to_timestamp()
        monthly_apps = df.groupby('Month').size().reset_index()
        monthly_apps.columns = ['Mois', 'Applications']

        monthly_fig = px.bar(
            monthly_apps,
            x='Mois',
            y='Applications',
            title='Candidatures par mois'
        )
        monthly_fig.update_layout(
            xaxis_tickformat="%b %Y",
            xaxis_tickangle=-45
        )

        monthly_fig.update_layout(xaxis_tickangle=-45)

        daily_apps = df.groupby(df[date_applied_col].dt.floor("D")).size().reset_index()
        daily_apps.columns = ['Date', 'Applications']

        daily_apps_sorted = daily_apps.sort_values('Date')
        daily_apps_sorted['Cumulative'] = daily_apps_sorted['Applications'].cumsum()

        cumulative_fig = px.area(
            daily_apps_sorted,
            x='Date',
            y='Cumulative',
            title='Candidatures cumulées'
        )


        return {
            "timeline": json.dumps(timeline_fig, cls=plotly.utils.PlotlyJSONEncoder),
            "hourly": json.dumps(hourly_fig, cls=plotly.utils.PlotlyJSONEncoder),
            "daily": json.dumps(daily_fig, cls=plotly.utils.PlotlyJSONEncoder),
            "monthly": json.dumps(monthly_fig, cls=plotly.utils.PlotlyJSONEncoder),
            "cumulative": json.dumps(cumulative_fig, cls=plotly.utils.PlotlyJSONEncoder)
        }

    def calculate_date_statistics(self, date_applied_col: str = "Date Applied", n_digits: int = 2) -> dict:
        """Calculate useful statistics from date data."""
        df = self.job_application_df.copy()
        df[date_applied_col] = pd.to_datetime(df[date_applied_col], utc=True)

        today = pd.Timestamp.now(tz="UTC").normalize()

        current_day = df[
            (df[date_applied_col] >= today) &
            (df[date_applied_col] < today + pd.Timedelta(days=1))
        ]
        current_week = df[df[date_applied_col] >= today - pd.Timedelta(days=6)]

        print(len(f"Number of applications today: {current_day}"))
        most_active_hour = df[date_applied_col].dt.hour.mode().iloc[0]
        most_active_day = df[date_applied_col].dt.day_name().mode().iloc[0]

        date_range = (df[date_applied_col].max() - df[date_applied_col].min()).days + 1
        avg_per_day = len(df) / date_range if date_range > 0 else 0

        resp_rate = len(df) / len(df[df["Status"] != "Applied"])

        return {
            "current_day": len(current_day),
            "current_week": len(current_week),
            "most_active_hour": f"{most_active_hour}h",
            "most_active_day": most_active_day,
            "avg_per_day": round(avg_per_day, n_digits),
            "total_days": date_range,
            "first_application": df['Date Applied'].min().strftime('%d/%m/%Y'),
            "last_application": df['Date Applied'].max().strftime('%d/%m/%Y'),
            "response_rate": round(resp_rate, n_digits),
            "total": len(df),
            "cities": self.locations_found_df["city_clean"].nunique(),
        }

    def create_all_dashboards(self) -> dict:
        """
        Create all dashboards and return them as a dictionary.

        Returns:
            dict: Dictionary containing all generated dashboards.
        """

        return {
            "map": self.create_map_dashboard(),
            "skills_pie": self.plot_skills_pie(),
            "url_pie": self.plot_url_pie(),
            "timeline_dashboards": self.create_comprehensive_timeline_dashboard(),
            "general_stats": self.calculate_date_statistics()
        }
