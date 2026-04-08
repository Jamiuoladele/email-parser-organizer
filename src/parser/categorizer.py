import re


class EmailCategorizer:

    def categorize(self, email):
        text = (email.subject + " " + email.body).lower()

        if any(word in text for word in ["invoice", "meeting", "project", "deadline"]):
            email.category = "Work"
        elif any(word in text for word in ["family", "party", "friend", "birthday"]):
            email.category = "Personal"
        else:
            email.category = "Other"

        return email