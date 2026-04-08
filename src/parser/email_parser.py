import re
from datetime import datetime

class Email:
    def __init__(self, sender, subject, body):
        self.sender = sender
        self.subject = subject
        self.body = body
        self.category = "Other"
        self.extracted_data = {"phones": [], "emails": [], "dates": []}

    def extract_data(self):
        # Phones
        phone_pattern = r"\+?\d[\d\s\-]{7,}\d"
        self.extracted_data["phones"] = re.findall(phone_pattern, self.body)

        # Emails (FIXED)
        email_pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
        self.extracted_data["emails"] = re.findall(email_pattern, self.body)

        # Dates
        date_pattern = r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b"
        self.extracted_data["dates"] = re.findall(date_pattern, self.body) 
                                                             

    def parse(self):
        """
        For now, parsing just ensures data is structured.
        Later, we can clean or extract more info.
        """
        return {
            "sender": self.sender,
            "subject": self.subject,
            "body": self.body,
            "category": self.category
        }