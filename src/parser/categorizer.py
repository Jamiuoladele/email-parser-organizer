import re


class EmailCategorizer:

    def categorize(self, email):
        text = (email.subject + " " + email.body).lower()

        if re.search(r"(meeting|project|deadline)", text):
            email.category = "Work"
        elif re.search(r"(discount|offer|sale)", text):
            email.category = "Promotion"
        elif re.search(r"(friend|party|weekend)", text):
            email.category = "Personal"
        else:
            email.category = "Other"

        return email