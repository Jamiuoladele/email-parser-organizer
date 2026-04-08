import json
from openpyxl import Workbook


def save_emails(emails, filename="data/emails.json"):
    try:
        data = []

        for email in emails:
            data.append({
                "sender": email.sender,
                "subject": email.subject,
                "body": email.body,
                "category": email.category
            })

        with open(filename, "w") as file:
            json.dump(data, file, indent=4)

        print("Emails saved successfully!")



    except Exception as e:
        print("Error saving emails:", e)


#  NEW FEATURE
def export_to_excel(emails, filename="export.xlsx"):
    try:
        wb = Workbook()
        ws = wb.active

        # Header row
        ws.append(["Sender", "Subject", "Category", "Extracted"])

        for email in emails:
            extracted = ""

            if email.extracted_data.get("phones"):
                extracted += "Phone: " + ", ".join(email.extracted_data["phones"]) + " "

            if email.extracted_data.get("emails"):
                extracted += "Email: " + ", ".join(email.extracted_data["emails"]) + " "

            if email.extracted_data.get("dates"):
                extracted += "Date: " + ", ".join(email.extracted_data["dates"])

            ws.append([
                email.sender,
                email.subject,
                email.category,
                extracted.strip()
            ])

        wb.save(filename)
        print("Excel exported successfully!")

    except Exception as e:
        print("Error exporting Excel:", e)