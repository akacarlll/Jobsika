"""This module is used to contain the base class for scraper"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class JobScraper:
    """Base class for job scrapers"""

    def __init__(self, url):
        self.url = url
        self.driver = self.setup_webdriver()

    def setup_webdriver(self) -> webdriver.Chrome:
        """Sets up the Selenium WebDriver with download preferences.

                Returns:
                    WebDriver: The configured Chrome WebDriver instance.
        """
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--blink-settings=imagesEnabled=false")
        options.add_argument("--headless=new")
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

    def scrape_job(self) -> str:
        """
        Scrapes the job offer text from the given URL using Selenium.

        Returns:
            str: The text content of the job offer.
        """
        self.driver.get(self.url)

        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        job_text = self.driver.find_element(By.TAG_NAME, "body").text
        return job_text