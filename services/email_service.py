import os
import smtplib
from datetime import datetime
from email.message import EmailMessage


def send_emergency_alerts(user, contacts, emergency):
    email_user = os.getenv("EMAIL_ADDRESS")
    email_pass = os.getenv("EMAIL_PASSWORD")

    print("DEBUG email_user =", email_user)
    print("DEBUG password exists =", bool(email_pass))

    if not email_user or not email_pass:
        print("Email credentials are not configured. Skipping emergency email alerts.")
        return

    subject = f"🚨 Emergency Alert from {user.full_name}"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = (
        "Emergency Alert Triggered\n\n"
        f"User: {user.full_name}\n"
        f"Time: {timestamp}\n\n"
        "Current Location:\n"
        f"Latitude: {emergency.latitude}\n"
        f"Longitude: {emergency.longitude}\n\n"
        "Google Maps:\n"
        f"https://www.google.com/maps?q={emergency.latitude},{emergency.longitude}\n\n"
        "This person may need immediate assistance.\n"
        "Please contact them or emergency services if necessary.\n\n"
        "Sent automatically by Emergency Response App."
    )

    for contact in contacts:
        if not contact.email:
            continue

        try:
            print(f"DEBUG sending emergency alert to {contact.email}")
            message = EmailMessage()
            message["Subject"] = subject
            message["From"] = email_user
            message["To"] = contact.email
            message.set_content(body)

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(email_user, email_pass)
                smtp.send_message(message)
            print(f"DEBUG email sent to {contact.email}")
        except Exception as exc:
            print(f"Failed to send alert to {contact.email}: {exc}")
