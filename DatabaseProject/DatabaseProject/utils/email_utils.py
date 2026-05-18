import smtplib
from email.message import EmailMessage

def send_receipt_email(to_email, pdf_path):
    msg = EmailMessage()
    msg['Subject'] = "Your Bookstore Receipt"
    msg['From'] = "hiradnabilety17@gmail.com"
    msg['To'] = to_email
    msg.set_content("Thank you for your purchase! Your receipt is attached.")

    with open(f"static/{pdf_path}", "rb") as f:
        msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename=pdf_path)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("hiradnabilety17@gmail.com", "qktq mlnd pbje nlqw")
        smtp.send_message(msg)
