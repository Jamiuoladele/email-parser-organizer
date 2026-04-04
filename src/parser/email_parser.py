import re


class Email:
    def __init__(self, sender, subject, body):
        self.sender = sender
        self.subject = subject
        self.body = body
        self.category = "other"
        self.extracted_data = {}

    def extract_data(self):
        phones = re.findall(r'\b0\{10}\b',self.body)
        emails = re.findall(r'\b[\w\.-]+@[\w\.-]+\.\w+\b',self.body)
        dates = re.findall(r"\b\d{2}/\d{2}/\d{2}/\d{4}\b",self.body)

        self.extracted_data  = {
            "phones": phones,
            "emails": emails,
            "dates":dates
        }

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