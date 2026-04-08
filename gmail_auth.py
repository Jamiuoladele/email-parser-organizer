# import imaplib
# import email
# from email.header import decode_header

# CONFIGURATION 
# EMAIL = "your_email@gmail.com"          #  Replace with your Gmail
# APP_PASSWORD = "your_app_password"      #  Replace with your Gmail App Password
# MAX_EMAILS = 5                           # Number of latest emails to fetch

# CONNECT TO GMAIL
# def connect_gmail():
#     mail = imaplib.IMAP4_SSL("imap.gmail.com")
#     mail.login(EMAIL, APP_PASSWORD)
#     mail.select("inbox")
#     return mail

#FETCH EMAILS
# def fetch_emails(mail, max_emails=MAX_EMAILS):
#     status, messages = mail.search(None, "ALL")
#     messages = messages[0].split()
    
#     for num in messages[-max_emails:]:
#         status, msg_data = mail.fetch(num, "(RFC822)")
#         msg = email.message_from_bytes(msg_data[0][1])
        
#         # Decode subject
#         subject, encoding = decode_header(msg["subject"])[0]
#         if isinstance(subject, bytes):
#             subject = subject.decode(encoding if encoding else "utf-8")
        
#         # Decode sender
#         from_ = msg.get("from")
        
#         # Get the email body
#         body = ""
#         if msg.is_multipart():
#             for part in msg.walk():
#                 if part.get_content_type() == "text/plain":
#                     body = part.get_payload(decode=True).decode()
#                     break
#         else:
#             body = msg.get_payload(decode=True).decode()
        
#         print("From:", from_)
#         print("Subject:", subject)
#         print("Body Preview:", body[:100], "...")  # Show first 100 chars
#         print("-" * 50)

#MAIN
# def main():
#     mail = connect_gmail()
#     fetch_emails(mail)

# if __name__ == "__main__":
#     main()