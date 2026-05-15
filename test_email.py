import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

email_user = os.getenv("EMAIL_ADDRESS")
email_pass = os.getenv("EMAIL_PASSWORD")

print(f"EMAIL_ADDRESS: {email_user}")
print(f"PASSWORD exists: {bool(email_pass)}")

if not email_user or not email_pass:
    print("Credentials not set")
    exit(1)

try:
    message = EmailMessage()
    message["Subject"] = "Test Email"
    message["From"] = email_user
    message["To"] = "hiradnabilety17@gmail.com"  # One of the emergency emails
    message.set_content("This is a test email from the Emergency App.")

    print("Attempting to send test email...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(email_user, email_pass)
        smtp.send_message(message)
    print("Test email sent successfully!")
except Exception as e:
    print(f"Failed to send email: {e}")