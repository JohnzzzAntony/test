"""
orders/notifications.py  ← REPLACE your existing file
=======================================================
Delegates all e-mail sending to accounts.email_notifications.
SMS and WhatsApp stubs preserved for future integration.
"""

import logging

logger = logging.getLogger(__name__)


def send_customer_notification(order, is_automated=True, notification_type="status_change"):
    """
    Main notification dispatcher for order events.

    Parameters
    ----------
    order             : orders.models.CustomerOrder
    is_automated      : bool  (backward-compat, unused internally)
    notification_type : 'order_placed' | 'payment_confirmation' | 'status_change'

    Called automatically from CustomerOrder.save() in orders/models.py.
    Can also be called manually — e.g. from a Stripe webhook view:

        from orders.notifications import send_customer_notification
        send_customer_notification(order, notification_type='payment_confirmation')
    """
    try:
        from core.models import SiteSettings
        site_config = SiteSettings.objects.first()
        if not site_config:
            logger.warning("No SiteSettings found — skipping notification for order %s", order.pk)
            return

        # ── E-mail ────────────────────────────────────────────────────────────
        if site_config.enable_email_notifications:
            from accounts.email_notifications import send_order_email
            send_order_email(order, notification_type=notification_type)

        # ── SMS (placeholder — wire up Twilio / Vonage here) ─────────────────
        if getattr(site_config, "enable_sms_notifications", False) and order.phone:
            logger.info("SMS notification triggered for order %s", order.pk)
            # from twilio.rest import Client
            # client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            # client.messages.create(
            #     body=f"JKR-{order.pk:05d} status: {order.get_status_display()}",
            #     from_=settings.TWILIO_PHONE_NUMBER,
            #     to=order.phone,
            # )

        # ── WhatsApp (placeholder) ────────────────────────────────────────────
        if getattr(site_config, "enable_whatsapp_notifications", False) and order.phone:
            logger.info("WhatsApp notification triggered for order %s", order.pk)

    except Exception as exc:
        logger.error("Notification error for order %s: %s", order.pk, exc)
