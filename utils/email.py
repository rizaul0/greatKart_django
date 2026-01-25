# utils/email.py
from email.message import EmailMessage
from django.core.mail import send_mail
from django.conf import settings
import threading

def send_email_async(subject, message, recipients):
    def task():
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipients=recipients,
                fail_silently=True,  # IMPORTANT
            )
        except Exception:
            pass  # Never crash the request

    threading.Thread(target=task).start()




def send_invoice_email_async(order, pdf_buffer):
    def task():
        try:
            email = EmailMessage(
                subject="Your GreatKart Invoice",
                body="Thank you for your order.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[order.user.email],
            )
            email.attach(
                f"Invoice_{order.order_number}.pdf",
                pdf_buffer.getvalue(),
                "application/pdf",
            )
            email.send(fail_silently=True)
        except Exception:
            pass

    threading.Thread(target=task, daemon=True).start()
