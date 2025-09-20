from jobs_engine.scraper.site_scrapers import WelcomeToTheJungleScraper
from jobs_engine.scraper import JobScraper



SCRAPERS_DICT = {"welcome_to_the_jungle": WelcomeToTheJungleScraper,
                 "unknown" : JobScraper}