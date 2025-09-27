from django.test import TestCase

from jobs_engine.scraper import JobScraper


class TestJobScraper(TestCase):
    def test_selenium_scraper(self):
        mock_url = "https.fake_site.com"
        scraper = JobScraper(mock_url)
        assert scraper.driver is None
