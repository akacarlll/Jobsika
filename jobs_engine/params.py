from jobs_engine.scraper import JobScraper
from jobs_engine.scraper.site_scrapers import HelloWorkScraper, WelcomeToTheJungleScraper

SCRAPERS_DICT = {"welcometothejungle": WelcomeToTheJungleScraper,
                 "hellowork": HelloWorkScraper,
                 "unknown" : JobScraper}

AVAILABLE_SITE_FOR_SCRAPING = [
        "welcometothejungle"
        "hellowork"
]
