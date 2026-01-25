# utils/email.py

import threading
import requests
import base64
from django.conf import settings

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


def _normalize_recipients(recipients):
    """
    Accepts:
    - string email
    - list/tuple of emails
    Returns a clean list of emails
    """
    if isinstance(recipients, str):
        return [recipients]
    return [email for email in recipients if email]


def send_email_async(subject, message, recipients):
    if isinstance(recipients, str):
        recipients = [recipients]

    payload = {
        "sender": {
            "name": "GreatKart",
            "email": settings.DEFAULT_FROM_EMAIL,
        },
        "to": [{"email": email} for email in recipients],
        "subject": subject,
        "htmlContent": f"<p>{message}</p>",
    }

    headers = {
        "api-key": settings.BREVO_API_KEY,
        "Content-Type": "application/json",
        "accept": "application/json",
    }

    response = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        json=payload,
        headers=headers,
        timeout=15,
    )

    print("BREVO STATUS:", response.status_code)
    print("BREVO RESPONSE:", response.text)

    def task():
        try:
            recipient_list = _normalize_recipients(recipients)

            payload = {
                "sender": {
                    "name": "GreatKart",
                    "email": settings.DEFAULT_FROM_EMAIL,
                },
                "to": [{"email": email} for email in recipient_list],
                "subject": subject,
                "htmlContent": f"<p>{message}</p>",
            }

            headers = {
                "api-key": settings.BREVO_API_KEY,
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            response = requests.post(
                BREVO_API_URL,
                json=payload,
                headers=headers,
                timeout=15,
            )

            if response.status_code not in (200, 201, 202):
                print("Brevo API error:", response.status_code, response.text)

        except Exception as e:
            print("Email API exception:", e)

    threading.Thread(target=task, daemon=True).start()


def send_invoice_email_async(order, pdf_buffer):
    def task():
        try:
            email = order.user.email
            if not email:
                return

            attachment = {
                "content": base64.b64encode(pdf_buffer.getvalue()).decode(),
                "name": f"Invoice_{order.order_number}.pdf",
            }

            payload = {
                "sender": {
                    "name": "GreatKart",
                    "email": settings.DEFAULT_FROM_EMAIL,
                },
                "to": [{"email": email}],
                "subject": "Your GreatKart Invoice",
                "htmlContent": (
                    "<p>Thank you for your order. "
                    "Please find your invoice attached.</p>"
                ),
                "attachment": [attachment],
            }

            headers = {
                "api-key": settings.BREVO_API_KEY,
                "Content-Type": "application/json",
                "accept": "application/json",
            }

            response = requests.post(
                BREVO_API_URL,
                json=payload,
                headers=headers,
                timeout=20,
            )

            if response.status_code not in (200, 201, 202):
                print("Invoice email error:", response.status_code, response.text)

        except Exception as e:
            print("Invoice email exception:", e)

    threading.Thread(target=task, daemon=True).start()
