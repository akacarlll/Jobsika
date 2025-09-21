"""Main entry point for the job scraping and parsing application."""

from .scraper import JobScraper
from .job_parser.llm_client import LLMClient
from datetime import datetime
from .params import SCRAPERS_DICT, AVAILABLE_SITE_FOR_SCRAPING
import logging

logger = logging.getLogger(__name__)

class JobApplicationProcessor:
    """Processes job applications by scraping and parsing job offers."""

    def __init__(self, notes:str):
        self.notes = notes
        self.url = ""
        self.parser = LLMClient()

    def create_prompt(self, job_description: str) -> str:
        """
        Creates a prompt for the LLM based on the job text.

        Return: 
            str: The formatted prompt for the LLM.
        """

        template = """
            Extract the following information from the job offer:
            1. Job Title: The title of the job position.
            2. Company Name: The name of the company offering the job.
            3. Location: The job's location (city, state, country, or remote).
            4. Required Skills: A list of specific skills or qualifications required (e.g., ["Python", "SQL", "Docker"]).
            5. Job Description Summary: A concise summary of the job responsibilities and role (2-3 sentences).
            6. Salary: The salary or compensation range, if explicitly stated.
            7. Contact Information: Any contact details provided for application or inquiries.
            8. Contract Type: The type of contract (e.g., CDI, CDD, freelance).

            Job Offer Text:
            {job_description}

            Please format the output as a JSON object with keys: 
            'job_title', 'company_name', 'location', 'required_skills', 'job_description_summary', 'salary', 'contact_information'.

            If any information is missing or unclear, use the following rules:
            - For 'job_title', 'company_name', 'location', and 'job_description_summary', provide an empty string ("") if not found.
            - For 'required_skills', provide an empty list ([]) if not found.
            - For 'salary', provide null if not found or if the salary is not explicitly stated.
        """
        return template.format(job_description=job_description)

    def get_site_to_scrape(self)-> str:
        """_summary_

        Returns:
            str: _description_
        """
        for available_site in AVAILABLE_SITE_FOR_SCRAPING:
            if available_site in self.url:
                return available_site
        return "unknown"

    def run_scraper(self) -> str:
        """_summary_

        Returns:
            JobScraper: _description_
        """
        scraper : JobScraper = SCRAPERS_DICT[self.get_site_to_scrape()](url=self.url)
        return scraper.scrape_job()

    def process_job_offer(self, job_description: str | None = None)-> dict:
        """
        Scrapes a job offer and generates a summary.

        job_description (str | None): The job description if the user sent it, 
            None if they used the URL method.
        Return:
            dict: A dict containaing the information from the Job post.
        """
        if not job_description:
            job_description = self.run_scraper()

        prompt = self.create_prompt(job_description)

        self.job_offer_dict = self.parser.generate(prompt)

        return self.add_element_to_job_offer()


    def add_element_to_job_offer(self) -> dict:
        """_summary_

        Returns:
            dict: _description_
        """
        now = datetime.now()
        self.job_offer_dict["application_date"] = now.strftime("%Y-%m-%d %H:%M:%S")
        self.job_offer_dict["url"] = self.url
        self.job_offer_dict["url"]
        self.job_offer_dict["required_skills"] = self.join_list_if_list(self.job_offer_dict["required_skills"])
        self.job_offer_dict["notes"] = self.notes
        return self.job_offer_dict



    def join_list_if_list(self, potential_list: str | list) -> str:
        """
        As the LLM aren't deteministic, they can output string or list even if we ask for a string.

        Args:
            potential_list (str | list): _description_

        Returns:
            str: _description_
        """
        if isinstance(potential_list, list):
            return ", ".join(potential_list)
        return potential_list




