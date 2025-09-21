"""This module is used to scrape job offers from Welcome to the Jungle"""

from ..base_scraper import JobScraper


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class WelcomeToTheJungleScraper(JobScraper):
    """Scraper for Welcome to the Jungle job offers"""

    def __init__(self, url):
        self.url = url
        self.driver = self.setup_webdriver()

    def scrape_job(self) -> str:
        """
        Scrapes the page text from the given URL using Selenium.

        Returns:
            str: The text content of the page, with the job offer content in it.
        """
        self.driver.get(self.url)

        accept_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "axeptio_btn_acceptAll"))
        )
        accept_button.click()

        job_text = self.driver.find_element(By.TAG_NAME, "body").text
        return job_text
