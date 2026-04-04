def fetch_emails():
    try:
        emails = [
            {"sender": "boss@company.com", "subject": "Meeting", "body": "Discuss project"},
            {"sender": "friend@gmail.com", "subject": "Weekend", "body": "Let's hang out"}
        ]

        return emails

    except Exception as e:
        print("Error fetching emails:", e)
        return []