import imaplib
import smtplib
import email
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

class EmailClient:
    def __init__(self):
        # Get credentials and sanitize them (remove non-ASCII characters)
        email_addr = os.getenv("EMAIL_USER") or os.getenv("EMAIL_ADDR")
        email_pass = os.getenv("EMAIL_PASS")

        # Clean credentials: replace non-breaking spaces and encode/decode to remove non-ASCII
        self.email_addr = email_addr.encode('ascii', 'ignore').decode('ascii').strip() if email_addr else None
        self.email_pass = email_pass.encode('ascii', 'ignore').decode('ascii').strip() if email_pass else None

        self.imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")

    def connect_imap(self):
        mail = imaplib.IMAP4_SSL(self.imap_server)
        mail.login(self.email_addr, self.email_pass)
        return mail

    def send_reply(self, to_addr, subject, body, message_id=None, is_html=False):
        if is_html:
            msg = MIMEMultipart('alternative')
            # Plain text fallback (could be stripped html)
            part1 = MIMEText("Please view this email in an HTML-compatible client.", 'plain', 'utf-8')
            part2 = MIMEText(body, 'html', 'utf-8')
            msg.attach(part1)
            msg.attach(part2)
        else:
            msg = MIMEText(body, 'plain', 'utf-8')

        msg['Subject'] = f"Re: {subject}" if not subject.startswith("Re:") else subject
        msg['From'] = self.email_addr
        msg['To'] = to_addr
        
        if message_id:
            msg['In-Reply-To'] = message_id
            msg['References'] = message_id

        with smtplib.SMTP_SSL(self.smtp_server, 465) as smtp:
            smtp.login(self.email_addr, self.email_pass)
            smtp.send_message(msg)

    def get_body(self, msg):
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    payload = part.get_payload(decode=True)
                    return payload.decode('utf-8', errors='ignore') if payload else ""
                elif content_type == "text/html":
                    payload = part.get_payload(decode=True)
                    if payload:
                        html = payload.decode('utf-8', errors='ignore')
                        soup = BeautifulSoup(html, "html.parser")
                        return soup.get_text()
        else:
            payload = msg.get_payload(decode=True)
            return payload.decode('utf-8', errors='ignore') if payload else ""
        return ""

    def check_emails(self):
        try:
            mail = self.connect_imap()
            mail.select('inbox')
            
            # Search for all Unseen emails
            status, response = mail.search(None, 'UNSEEN')
            
            emails = []
            if status == 'OK':
                for num in response[0].split():
                    # Fetch the email (RFC822 marks it as Read automatically)
                    # To prevent data loss on crash, one could use (BODY.PEEK[]) and mark read later.
                    # But for now, we stick to standard fetch to keep it simple.
                    typ, data = mail.fetch(num, '(RFC822)')
                    if typ == 'OK':
                        msg = email.message_from_bytes(data[0][1])
                        emails.append(msg)
            
            mail.close()
            mail.logout()
            return emails
        except Exception as e:
            print(f"Error checking emails: {e}")
            return []