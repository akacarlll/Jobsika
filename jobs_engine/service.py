"""Main entry point for the job scraping and parsing application."""

from .scraper.site_scrapers import WelcomeToTheJungleScraper
from .job_parser.llm_client import LLMClient
from pathlib import Path
import pandas as pd 
from datetime import datetime


class JobApplicationProcessor:
    """Processes job applications by scraping and parsing job offers."""

    def __init__(self, url: str):
        self.url = url
        self.scraper = WelcomeToTheJungleScraper(url=self.url)
        self.parser = LLMClient()
        self.job_db_path = Path("data/track_job.csv")

    def create_prompt(self, job_text: str) -> str:
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
            {job_text}

            Please format the output as a JSON object with keys: 
            'job_title', 'company_name', 'location', 'required_skills', 'job_description_summary', 'salary', 'contact_information'.

            If any information is missing or unclear, use the following rules:
            - For 'job_title', 'company_name', 'location', and 'job_description_summary', provide an empty string ("") if not found.
            - For 'required_skills', provide an empty list ([]) if not found.
            - For 'salary', provide null if not found or if the salary is not explicitly stated.
        """
        return template.format(job_text=job_text)
    

    def process_job_offer(self)-> dict:
        """
        Scrapes a job offer and generates a summary.

        Return:
            dict: A dict containaing the information from the Job post.
        """
        job_text = self.scraper.scrape_job()
        prompt = self.create_prompt(job_text)
        self.job_offer_dict = self.parser.generate(prompt)
        self.job_offer_dict["Application Date"] = datetime.now()
        self.job_offer_dict["URL"] = self.url
        return self.job_offer_dict

    def add_job_offer_to_db(self) -> None:
        """
        Add an entry to the job Database.
        """
        if Path.exists(self.job_db_path):
            job_db = pd.read_csv(self.job_db_path)
            new_row = pd.DataFrame([self.job_offer_dict])
            job_db = pd.concat([job_db, new_row], ignore_index=True)
        else :
            job_db = pd.DataFrame(self.job_offer_dict)
        job_db.to_csv(self.job_db_path)
        


        
