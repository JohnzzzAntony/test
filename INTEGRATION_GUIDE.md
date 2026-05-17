# JKR International — Email & Stripe Integration Guide

This document describes every integration added to the project, how to configure them, and how to test them end-to-end.

---

## 1. Email Integration

### What was added

| File | Change |
|------|--------|
| `accounts/email_notifications.py` | Fully rewritten — HTML email rendering, all notification types |
| `orders/notifications.py` | Dispatcher that routes to `send_order_email()` |
| `contact/views.py` | Contact form now sends admin alert + customer auto-reply |
| `core/models.py` | Added `admin_notification_email` field to `SiteSettings` |
| `templates/emails/` | 8 new HTML email templates (see below) |
| `.env.example` | Added `ADMIN_EMAIL` and `STRIPE_WEBHOOK_SECRET` variables |

### Email templates

| Template | Sent when |
|----------|-----------|
| `emails/welcome.html` | User registers a new account |
| `emails/order_placed.html` | Order is created (any payment method) |
| `emails/payment_confirmation.html` | Stripe/Tabby/Tamara payment confirmed |
| `emails/order_status_update.html` | Admin changes order status in the panel |
| `emails/contact_form_admin.html` | Admin receives a new contact form submission |
| `emails/contact_form_reply.html` | Customer receives auto-reply after submitting contact form |
| `emails/newsletter_welcome.html` | User subscribes to the newsletter |
| `emails/admin_new_order.html` | Admin receives new order alert |

### Configuration (`.env`)

```dotenv
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password   # Gmail App Password
DEFAULT_FROM_EMAIL=your-email@gmail.com
ADMIN_EMAIL=admin@yourdomain.com                 # Receives contact form + order alerts
```

**Gmail App Password setup:**
1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable 2-Step Verification
3. Go to [App Passwords](https://myaccount.google.com/apppasswords)
4. Create a new app password for "Mail"
5. Paste the 16-character password into `EMAIL_HOST_PASSWORD`

**Enable email notifications in admin panel:**
1. Go to `/admin/core/sitesettings/`
2. Check **Enable Email Notifications**
3. Set **Admin Notification Email** to the address that should receive alerts

### Testing email locally

To test without sending real emails, use Django's console backend:

```dotenv
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Emails will be printed to the terminal instead of sent.

---

## 2. Stripe Integration

### What was added / fixed

| File | Change |
|------|--------|
| `orders/views.py` | `checkout_payment` — passes `stripe_publishable_key` to template |
| `orders/views.py` | `stripe_webhook` — handles 3 event types, compatible with Stripe v15 |
| `templates/orders/checkout_payment.html` | Stripe.js loaded from CDN; publishable key injected |
| `.env.example` | Added `STRIPE_WEBHOOK_SECRET` |

### Stripe checkout flow

```
Customer selects "Card" → POST /enquiry-cart/checkout/payment/
    → stripe.checkout.Session.create(...)
    → Redirect to Stripe-hosted checkout page
    → On success: redirect to /enquiry-cart/checkout/success/?session_id=...
    → Stripe also fires webhook: POST /enquiry-cart/stripe-webhook/
        → order.payment_status = 'paid'
        → Payment confirmation email sent to customer
```

### Configuration (`.env`)

```dotenv
STRIPE_PUBLISHABLE_KEY=pk_test_...    # From Stripe Dashboard → Developers → API keys
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...       # From Stripe Dashboard → Developers → Webhooks
```

### Setting up the Stripe webhook

1. Go to [Stripe Dashboard → Webhooks](https://dashboard.stripe.com/webhooks)
2. Click **Add endpoint**
3. Set the endpoint URL to: `https://yourdomain.com/enquiry-cart/stripe-webhook/`
4. Select these events:
   - `checkout.session.completed`
   - `checkout.session.expired`
   - `payment_intent.payment_failed`
5. Copy the **Signing secret** (`whsec_...`) and add it to `.env` as `STRIPE_WEBHOOK_SECRET`

### Testing Stripe locally with Stripe CLI

```bash
# Install Stripe CLI: https://stripe.com/docs/stripe-cli
stripe login
stripe listen --forward-to localhost:8000/enquiry-cart/stripe-webhook/
# In another terminal, trigger a test event:
stripe trigger checkout.session.completed
```

### Stripe webhook events handled

| Event | Action |
|-------|--------|
| `checkout.session.completed` | Sets `payment_status='paid'`, sends payment confirmation email |
| `checkout.session.expired` | Sets `payment_status='failed'` |
| `payment_intent.payment_failed` | Sets `payment_status='failed'` |

---

## 3. Admin Panel Configuration

After deploying, visit `/admin/` and configure:

1. **Core → Site Settings** — Set site name, email, phone, social links, enable email notifications, set admin notification email
2. **Core → Design Settings** — Customise colours, fonts, and layout
3. **Products** — Add categories, collections, and products
4. **Sliders** — Add homepage hero banners

---

## 4. Deployment Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Set a strong random `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Set `CSRF_TRUSTED_ORIGINS` to your HTTPS domain
- [ ] Configure `DATABASE_URL` for PostgreSQL
- [ ] Configure Cloudinary for media storage
- [ ] Add real Stripe **live** keys (`pk_live_...` / `sk_live_...`)
- [ ] Register the Stripe webhook endpoint for the live domain
- [ ] Configure SMTP email credentials
- [ ] Run `python manage.py migrate`
- [ ] Run `python manage.py collectstatic`
- [ ] Create a superuser: `python manage.py createsuperuser`
- [ ] Create a `SiteSettings` record in the admin panel
- [ ] Create a `DesignSettings` record in the admin panel

---

## 5. Key URLs

| URL | Description |
|-----|-------------|
| `/` | Homepage |
| `/products/` | Product listing |
| `/enquiry-cart/cart/` | Shopping cart |
| `/enquiry-cart/checkout/billing/` | Checkout — billing step |
| `/enquiry-cart/checkout/payment/` | Checkout — payment step |
| `/enquiry-cart/checkout/success/` | Order success page |
| `/enquiry-cart/stripe-webhook/` | Stripe webhook endpoint |
| `/contact/` | Contact form |
| `/accounts/login/` | Customer login |
| `/accounts/register/` | Customer registration |
| `/admin/` | Admin panel |
