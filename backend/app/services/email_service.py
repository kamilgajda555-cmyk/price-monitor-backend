import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)

def send_email(to_email: str, subject: str, html_content: str):
    """Send email via SMTP"""
    
    if not SMTP_USER or not SMTP_PASSWORD:
        logger.warning("SMTP credentials not configured, skipping email")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SMTP_FROM
        msg['To'] = to_email
        
        html_part = MIMEText(html_content, 'html')
        msg.attach(html_part)
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email sent to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False

def send_alert_email(to_email: str, product_name: str, message: str):
    """Send price alert email"""
    
    subject = f"Price Alert: {product_name}"
    
    html_content = f"""
    <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Price Monitor Alert</h1>
                </div>
                <div class="content">
                    <h2>{product_name}</h2>
                    <p>{message}</p>
                    <p>This is an automated alert from your Price Monitor system.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Price Monitor. All rights reserved.</p>
                </div>
            </div>
        </body>
    </html>
    """
    
    return send_email(to_email, subject, html_content)

def send_report_email(to_email: str, report_type: str, attachment_path: str = None):
    """Send report via email"""
    
    subject = f"Price Monitor Report: {report_type}"
    
    html_content = f"""
    <html>
        <body>
            <h2>Your {report_type} report is ready</h2>
            <p>Please find your requested report attached to this email.</p>
            <p>Report generated at: {os.path.basename(attachment_path) if attachment_path else 'N/A'}</p>
        </body>
    </html>
    """
    
    # TODO: Add attachment support
    return send_email(to_email, subject, html_content)
