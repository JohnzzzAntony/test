"""
accounts/email_notifications.py  (NEW FILE)
============================================
Single source of truth for all transactional e-mails in the JKR project.

Covers
------
  send_welcome_email(user)                          — on registration / first OAuth sign-in
  send_login_alert(user, request)                   — on every login
  send_order_email(order, notification_type)        — order placed, payment confirmed, status changes

All sends run in a background daemon thread so they never block a request.
"""

import logging
import threading

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _site_name():
    try:
        from core.models import SiteSettings
        cfg = SiteSettings.objects.first()
        if cfg and cfg.site_name:
            return cfg.site_name
    except Exception:
        pass
    return "JKR International"


def _site_url():
    return getattr(settings, "SITE_URL", "http://localhost:8000")


def _currency():
    return getattr(settings, "CURRENCY", "AED")


def _emails_enabled():
    try:
        from core.models import SiteSettings
        cfg = SiteSettings.objects.first()
        if cfg:
            return bool(cfg.enable_email_notifications)
    except Exception:
        pass
    return True   # default ON if SiteSettings table not yet available


def _from_email():
    addr = getattr(settings, "DEFAULT_FROM_EMAIL", "") or getattr(settings, "EMAIL_HOST_USER", "")
    return addr


def _fire(subject: str, body: str, to: str):
    """Send an e-mail. In DEBUG mode, this is synchronous to help troubleshoot."""
    if not to:
        logger.warning("Email skipped: No recipient address provided.")
        return

    # Check if we should use background threads
    use_thread = not getattr(settings, "DEBUG", False)

    def _worker():
        try:
            logger.info("Attempting to send email to %s | Subject: %s", to, subject)
            send_mail(
                subject=subject,
                message=body,
                from_email=_from_email(),
                recipient_list=[to],
                fail_silently=False,
            )
            logger.info("✅ Email sent successfully → %s", to)
        except Exception as exc:
            logger.error("❌ Email failed → %s | Error: %s", to, exc)
            if settings.DEBUG:
                # In debug mode, we want to know why it failed
                import traceback
                traceback.print_exc()

    if use_thread:
        t = threading.Thread(target=_worker, daemon=True)
        t.start()
    else:
        _worker()


def test_email_connection(to_email=None):
    """Utility to test the SMTP connection and credentials."""
    site = _site_name()
    target = to_email or _from_email()
    subject = f"🔔 Test Email from {site}"
    body = f"SMTP configuration is working correctly!\n\nHost: {settings.EMAIL_HOST}\nPort: {settings.EMAIL_PORT}\nUser: {settings.EMAIL_HOST_USER}"
    
    logger.info("Running SMTP connection test...")
    _fire(subject, body, target)
    return f"Test email triggered for {target}. Check your console/logs for results."


def _get_client_ip(request):
    try:
        xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "Unknown")
    except Exception:
        return "Unknown"


# ─── Welcome e-mail ───────────────────────────────────────────────────────────

def send_welcome_email(user):
    """
    Send a welcome e-mail to a newly registered user.
    Called from register_view (password sign-up) and social_callback (first OAuth login).
    """
    if not user.email or not _emails_enabled():
        return

    name      = user.get_full_name() or user.username
    site      = _site_name()
    site_url  = _site_url()

    subject = f"Welcome to {site}! 🎉"
    body = f"""Dear {name},

Welcome to {site}! We're delighted to have you on board.

Your account is now active and ready to use.

  ▸ Shop our products : {site_url}/products/
  ▸ View your profile : {site_url}/accounts/profile/
  ▸ Track your orders : {site_url}/accounts/orders/

Account details
───────────────────────────────────────
Username : {user.username}
Email    : {user.email}

If you did not create this account, please ignore this message.

Warm regards,
The {site} Team
{site_url}
"""
    _fire(subject, body.strip(), user.email)


# ─── Login alert ──────────────────────────────────────────────────────────────

def send_login_alert(user, request):
    """
    Send a login-alert e-mail every time a user signs in.
    Called from the user_logged_in signal in signals.py.
    """
    if not user.email or not _emails_enabled():
        return

    name     = user.get_full_name() or user.username
    site     = _site_name()
    site_url = _site_url()
    now      = timezone.now().strftime("%Y-%m-%d %H:%M:%S")
    ip       = _get_client_ip(request)

    subject = f"New Login to Your {site} Account"
    body = f"""Dear {name},

We noticed a new login to your {site} account.

Login Details
───────────────────────────────────────
Username   : {user.username}
Email      : {user.email}
Time       : {now} (Dubai / UTC+4)
IP Address : {ip}

If this was you, no action is needed.
If you don't recognise this activity, please change your password immediately:
{site_url}/accounts/password/change/

Warm regards,
The {site} Team
{site_url}
"""
    _fire(subject, body.strip(), user.email)


# ─── Order e-mails ────────────────────────────────────────────────────────────

_STATUS_DETAIL = {
    "pending":             "Your order has been received and is being reviewed.",
    "packaging":           "Your order is being carefully packaged by our team.",
    "ready_for_shipment":  "Your order is packed and ready — our courier will collect it shortly.",
    "shipped":             "Great news! Your order is on its way to you.",
    "delivered":           "Your order has been delivered. We hope you love it! 🎉",
    "return_to_origin":    "Your order is being returned to our warehouse. Our team will be in touch.",
    "refund":              "Your refund is being processed. It may take 5-10 business days to appear.",
}

_STATUS_SUBJECT = {
    "order_placed":         "Order Confirmed",
    "payment_confirmation": "Payment Confirmed ✔",
    "pending":              "Order Received",
    "packaging":            "Your Order is Being Packaged",
    "ready_for_shipment":   "Your Order is Ready for Shipment",
    "shipped":              "Your Order is On Its Way 🚚",
    "delivered":            "Your Order Has Been Delivered 🎉",
    "return_to_origin":     "Order Return Update",
    "refund":               "Your Refund is Being Processed",
}


def send_order_email(order, notification_type: str = "status_change"):
    """
    Send an order-related e-mail to the customer.

    Parameters
    ----------
    order             : orders.models.CustomerOrder instance
    notification_type : str
        'order_placed'          — new order created
        'payment_confirmation'  — call manually after payment webhook success
        'status_change'         — any status update (reads order.status)
    """
    if not order.email or not _emails_enabled():
        return

    site      = _site_name()
    site_url  = _site_url()
    currency  = _currency()
    order_id  = f"JKR-{order.pk:05d}"
    customer  = f"{order.first_name} {order.last_name}".strip()
    tracking  = f"{site_url}/enquiry-cart/track/{order.pk}/"

    # ── Subject ───────────────────────────────────────────────────────────────
    if notification_type == "order_placed":
        subject_prefix = _STATUS_SUBJECT["order_placed"]
    elif notification_type == "payment_confirmation":
        subject_prefix = _STATUS_SUBJECT["payment_confirmation"]
    else:
        subject_prefix = _STATUS_SUBJECT.get(
            order.status, f"Order Update – {order.get_status_display()}"
        )
    subject = f"{subject_prefix} – Order #{order_id}"

    # ── Body ──────────────────────────────────────────────────────────────────
    address_block = (
        f"{order.street}\n"
        f"{order.city}, {order.emirates}\n"
        f"{order.country}\n"
        f"Phone: {order.phone}"
    )

    if notification_type == "payment_confirmation":
        body = f"""Dear {customer},

Your payment has been confirmed and your order is now being processed.

Payment Details
───────────────────────────────────────
Order Number   : #{order_id}
Total Amount   : {order.total_amount} {currency}
Payment Method : {order.get_payment_method_display()}
Payment Status : Paid ✔

Shipping Address
───────────────────────────────────────
{address_block}

Track your order → {tracking}

Thank you for choosing {site}!

Warm regards,
The {site} Team
{site_url}
"""

    elif notification_type == "order_placed":
        # Build item list
        item_lines = ""
        try:
            for item in order.items.select_related("product").all():
                item_lines += (
                    f"  • {item.product_name} × {item.quantity}"
                    f"  —  {item.total_price} {currency}\n"
                )
        except Exception:
            item_lines = "  (item details unavailable)\n"

        body = f"""Dear {customer},

Thank you for your order! We've received it and it is being processed.

Order Details
───────────────────────────────────────
Order Number   : #{order_id}
Payment Method : {order.get_payment_method_display()}
Status         : {order.get_status_display()}

Items Ordered
───────────────────────────────────────
{item_lines}
Order Total    : {order.total_amount} {currency}

Shipping Address
───────────────────────────────────────
{address_block}

Track your order → {tracking}

We'll keep you updated at every step of the journey.

Thank you for choosing {site}!

Warm regards,
The {site} Team
{site_url}
"""

    else:   # status_change
        status_msg = _STATUS_DETAIL.get(
            order.status,
            f"Your order status has been updated to: {order.get_status_display()}."
        )
        body = f"""Dear {customer},

{status_msg}

Order Details
───────────────────────────────────────
Order Number   : #{order_id}
Current Status : {order.get_status_display()}
Total Amount   : {order.total_amount} {currency}

Shipping Address
───────────────────────────────────────
{address_block}

Track your order → {tracking}

Thank you for choosing {site}!

Warm regards,
The {site} Team
{site_url}
"""

    _fire(subject, body.strip(), order.email)
