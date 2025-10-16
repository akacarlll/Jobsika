"""This module is used to deal with google sheet API, adding, deleting modifying sheets and rows"""

import logging
from typing import ClassVar, Optional

import requests

logger = logging.getLogger(__name__)

class GoogleSheetsManager:
    """Manager class for Google Sheets API operations."""

    SPREADSHEET_NAME = "JobsikaTracker"
    SHEET_NAME = "ApplicationTracker"

    BASE_HEADERS : ClassVar = [
        "Job Title",
        "Company",
        "Location",
        "URL",
        "Date Applied",
        "Salary",
        "Skills Required",
        "Contact Information",
        "Job Description",
        "Notes",
        "Status",
        "Number of Interview",
        "Experience",
        "Contract Type",
    ]

    STATUS_VALUES : ClassVar = [
        "Applied",
        "In Progress",
        "Interviewing",
        "Offer Received",
        "Accepted",
        "Rejected",
        "Withdrawn",
        "Paused",
        "Ignored",
        "Other",
    ]

    INTERVIEW_COUNT_VALUES : ClassVar = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    def get_or_create_spreadsheet(self) -> str:
        """
        Find existing spreadsheet or create new one.
        Returns the spreadsheet ID.
        """
        search_url = "https://www.googleapis.com/drive/v3/files"
        params = {
            "q": (f"name='{self.SPREADSHEET_NAME}' and mimeType='application/vnd.google-apps.spreadsheet'"
            "and trashed=false"),
            "fields": "files(id, name)",
        }

        response = requests.get(
            search_url, headers=self.headers, params=params, timeout=10
        )
        response.raise_for_status()

        files = response.json().get("files", [])

        if files:
            spreadsheet_id = files[0]["id"]
            logger.info(f"Found existing spreadsheet: {spreadsheet_id}")
            return spreadsheet_id

        logger.info("Creating new spreadsheet")
        return self.create_spreadsheet()

    def create_spreadsheet(self) -> str:
        """Create a new spreadsheet and return its ID."""
        url = "https://sheets.googleapis.com/v4/spreadsheets"

        payload = {
            "properties": {"title": self.SPREADSHEET_NAME},
            "sheets": [{"properties": {"title": self.SHEET_NAME}}],
        }

        response = requests.post(url, json=payload, headers=self.headers, timeout=10)
        response.raise_for_status()

        spreadsheet_id = response.json()["spreadsheetId"]
        logger.info(f"Created new spreadsheet: {spreadsheet_id}")

        self.initialize_sheet(spreadsheet_id)

        return spreadsheet_id

    def get_or_create_sheet(self, spreadsheet_id: str) -> Optional[int]:
        """
        Get sheet ID or create it if it doesn't exist.
        Returns the sheet ID (gid).
        """
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}"
        params = {"fields": "sheets(properties(sheetId,title))"}

        response = requests.get(url, headers=self.headers, params=params, timeout=10)
        response.raise_for_status()

        sheets = response.json().get("sheets", [])

        for sheet in sheets:
            if sheet["properties"]["title"] == self.SHEET_NAME:
                sheet_id = sheet["properties"]["sheetId"]
                logger.info(f"Found existing sheet: {self.SHEET_NAME} (ID: {sheet_id})")
                return sheet_id

        logger.info(f"Creating new sheet: {self.SHEET_NAME}")
        return self.create_sheet_in_spreadsheet(spreadsheet_id)

    def create_sheet_in_spreadsheet(self, spreadsheet_id: str) -> int:
        """Create a new sheet within an existing spreadsheet."""
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}:batchUpdate"

        payload = {
            "requests": [{"addSheet": {"properties": {"title": self.SHEET_NAME}}}]
        }

        response = requests.post(url, json=payload, headers=self.headers, timeout=10)
        response.raise_for_status()

        sheet_id = response.json()["replies"][0]["addSheet"]["properties"]["sheetId"]

        self.initialize_sheet(spreadsheet_id)

        return sheet_id

    def initialize_sheet(self, spreadsheet_id: str) -> None:
        """Add headers and data validation to the sheet."""
        range_name = f"{self.SHEET_NAME}!A1"
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}"

        payload = {"values": [self.BASE_HEADERS]}

        params = {"valueInputOption": "RAW"}

        response = requests.put(
            url, json=payload, headers=self.headers, params=params, timeout=10
        )
        response.raise_for_status()

        logger.info("Headers added to sheet")

        self.add_data_validation(spreadsheet_id)

    def add_data_validation(self, spreadsheet_id: str) -> None:
        """Add dropdown validation for Status and Number of Interview columns."""
        sheet_id = self.get_or_create_sheet(spreadsheet_id)

        status_col_index = self.BASE_HEADERS.index("Status")

        interview_col_index = self.BASE_HEADERS.index("Number of Interview")

        url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}:batchUpdate"

        payload = {
            "requests": [
                {
                    "setDataValidation": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 1,
                            "startColumnIndex": status_col_index,
                            "endColumnIndex": status_col_index + 1,
                        },
                        "rule": {
                            "condition": {
                                "type": "ONE_OF_LIST",
                                "values": [
                                    {"userEnteredValue": val}
                                    for val in self.STATUS_VALUES
                                ],
                            },
                            "showCustomUi": True,
                            "strict": True,
                        },
                    }
                },
                {
                    "setDataValidation": {
                        "range": {
                            "sheetId": sheet_id,
                            "startRowIndex": 1,
                            "startColumnIndex": interview_col_index,
                            "endColumnIndex": interview_col_index + 1,
                        },
                        "rule": {
                            "condition": {
                                "type": "ONE_OF_LIST",
                                "values": [
                                    {"userEnteredValue": str(val)}
                                    for val in self.INTERVIEW_COUNT_VALUES
                                ],
                            },
                            "showCustomUi": True,
                            "strict": True,
                        },
                    }
                },
            ]
        }

        response = requests.post(url, json=payload, headers=self.headers, timeout=10)
        response.raise_for_status()

        logger.info("Data validation added to Status and Number of Interview columns")

    def append_row(self, spreadsheet_id: str, data: dict) -> None:
        """
        Append a job application row to the sheet.
        This is the equivalent of the Apps Script doPost function.
        """
        self.get_or_create_sheet(spreadsheet_id)

        row_data = [
            data.get("job_title", ""),
            data.get("company_name", ""),
            data.get("location", ""),
            data.get("url", ""),
            data.get("application_date", ""),
            data.get("salary", ""),
            data.get("required_skills", ""),
            data.get("contact_information", ""),
            data.get("job_description_summary", ""),
            data.get("notes", ""),
            "Applied",
            "0",
            data.get("experience_level", ""),
            data.get("contract_type", ""),
        ]

        range_name = f"{self.SHEET_NAME}!A:N"
        url = f"https://sheets.googleapis.com/v4/spreadsheets/{spreadsheet_id}/values/{range_name}:append"

        payload = {"values": [row_data], "majorDimension": "ROWS"}

        params = {"valueInputOption": "USER_ENTERED", "insertDataOption": "INSERT_ROWS"}

        response = requests.post(
            url, json=payload, headers=self.headers, params=params, timeout=10
        )
        response.raise_for_status()

        logger.info(f"Successfully appended row: {row_data[0]}")
