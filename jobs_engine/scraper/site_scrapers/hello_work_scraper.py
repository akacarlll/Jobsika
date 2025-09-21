import requests
from bs4 import BeautifulSoup
import random

from ..base_scraper import JobScraper

class HelloWorkScraper(JobScraper):
    """Scraper for Hello Work job offers"""

    def __init__(self, url):
        self.url = url

    def scrape_job(self) -> str:
        """
        Scrapes the page text from the given URL using Selenium.

        Returns:
            str: The text content of the page, with the job offer content in it.
        """
        headers = self.get_random_header()
        response = requests.get(self.url, headers=headers)

        soup = BeautifulSoup(response.text, "html.parser")


        job_description_div = soup.find("div", class_="tw-layout-inner-grid tw-pb-12 sm:tw-pb-16")
        return job_description_div.get_text(separator="\n", strip=True) # type: ignore

    def get_random_header(self)-> dict:
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/120.0.0.0 Safari/537.36",

            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",

            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
            " Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",

            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko)"
            " Version/16.0 Safari/605.1.15",

            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/605.1.15"
            " (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
        ]

        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept-Language": random.choice(["en-US,en;q=0.9", "en-GB,en;q=0.8", "fr-FR,fr;q=0.7"]),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        return headers

