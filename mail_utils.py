import smtplib
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def send_email_alert(subject, body, to_email, attachment_path=None):
    sender_email = os.getenv("ALERT_EMAIL")
    sender_password = os.getenv("ALERT_PASSWORD")

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as f:
            file_data = f.read()
            file_name = os.path.basename(attachment_path)
            msg.add_attachment(file_data, maintype="image", subtype="jpeg", filename=file_name)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print("📧 Email alert sent!")
    except Exception as e:
        print("❌ Failed to send email:", e)