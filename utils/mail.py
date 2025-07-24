import smtplib
from email.mime.text import MIMEText


EMAIL_USER = "aayanalispear@gmail.com"
EMAIL_PASS = "rxsssdhkllhrqupp"

def send_email(email, subject, message_body):
    msg = MIMEText(message_body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = EMAIL_PASS

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.sendmail(EMAIL_USER, email, msg.as_string())
            print(f"✅ Email sent to {email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
