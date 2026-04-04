from src.ingestion.email_fetcher import fetch_emails
from src.parser.email_parser import Email
from src.parser.categorizer import EmailCategorizer
from src.storage.storage import save_emails


def display_emails(emails):
    for email in emails:
        print("-----")
        print("Sender:", email.sender)
        print("Subject:", email.subject)
        print("Category:", email.category)


def main():
    categorizer = EmailCategorizer()
    parsed_emails = []

    while True:
        print("\n--- Email Parser Menu ---")
        print("1. Fetch and process emails")
        print("2. Display emails")
        print("3. Save emails")
        print("4. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            try:
                print("Fetching emails...")

                emails = fetch_emails()
                parsed_emails.clear()

                for email in emails:
                    # safeguard in case keys are missing
                    email_obj = Email(
                        email.get("sender", "Unknown"),
                        email.get("subject", "No Subject"),
                        email.get("body", "")
                    )

                    categorizer.categorize(email_obj)
                    parsed_emails.append(email_obj)

                print("Emails processed successfully!")

            except Exception as e:
                print("Error during email processing:", e)

        elif choice == "2":
            if not parsed_emails:
                print("No emails available. Please process first.")
            else:
                display_emails(parsed_emails)

        elif choice == "3":
            if not parsed_emails:
                print("No emails to save. Process first.")
            else:
                try:
                    save_emails(parsed_emails)
                    print("Emails saved successfully!")
                except Exception as e:
                    print("Error saving emails:", e)

        elif choice == "4":
            print("Exiting program...")
            break

        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("Unexpected error occurred:", e)