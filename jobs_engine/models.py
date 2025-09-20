from django.db import models


class JobPosting(models.Model):
    job_title = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    url = models.URLField()
    required_skills = models.CharField(max_length=255)
    job_description_summary = models.CharField(max_length=500)
    salary = models.IntegerField()
    contact_information = models.CharField(max_length=255)
    creation_date = models.DateTimeField(auto_now_add=True)
