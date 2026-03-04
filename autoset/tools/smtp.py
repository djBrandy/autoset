"""SMTP email sending tool"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional

logger = logging.getLogger(__name__)

def send_email(
    to_email: str,
    subject: str,
    body: str,
    from_email: str = "security@company.com",
    from_name: str = "IT Security",
    smtp_server: str = "localhost",
    smtp_port: int = 25,
    use_tls: bool = False,
    username: Optional[str] = None,
    password: Optional[str] = None,
    html: bool = False
) -> dict:
    """Send phishing email via SMTP
    
    Args:
        to_email: Recipient email
        subject: Email subject
        body: Email body
        from_email: Sender email
        from_name: Sender name
        smtp_server: SMTP server address
        smtp_port: SMTP port
        use_tls: Use TLS encryption
        username: SMTP auth username
        password: SMTP auth password
        html: Send as HTML email
        
    Returns:
        dict with status
    """
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{from_name} <{from_email}>"
        msg['To'] = to_email
        
        # Attach body
        if html:
            msg.attach(MIMEText(body, 'html'))
        else:
            msg.attach(MIMEText(body, 'plain'))
        
        # Connect to SMTP server
        if use_tls:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
        
        # Authenticate if credentials provided
        if username and password:
            server.login(username, password)
        
        # Send email
        server.send_message(msg)
        server.quit()
        
        logger.info(f"Email sent to {to_email}")
        return {
            "success": True,
            "message": f"Email sent to {to_email}"
        }
        
    except Exception as e:
        logger.error(f"Email send failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Email send failed"
        }

def send_bulk_emails(
    recipients: List[str],
    subject: str,
    body: str,
    **kwargs
) -> dict:
    """Send bulk phishing emails
    
    Args:
        recipients: List of recipient emails
        subject: Email subject
        body: Email body
        **kwargs: Additional args for send_email
        
    Returns:
        dict with results
    """
    results = {
        "total": len(recipients),
        "sent": 0,
        "failed": 0,
        "errors": []
    }
    
    for recipient in recipients:
        result = send_email(recipient, subject, body, **kwargs)
        if result["success"]:
            results["sent"] += 1
        else:
            results["failed"] += 1
            results["errors"].append({
                "recipient": recipient,
                "error": result.get("error")
            })
    
    return results
