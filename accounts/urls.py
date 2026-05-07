"""
accounts/urls.py  ← REPLACE your existing file
================================================
Google OAuth routes removed.
Supabase social auth routes kept and working.
"""

from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # ── Standard auth ──────────────────────────────────────────────────────────
    path("register/",       views.register_view,       name="register"),
    path("login/",          views.login_view,           name="login"),
    path("logout/",         views.logout_view,          name="logout"),
    path("guest-checkout/", views.guest_checkout_view,  name="guest_checkout"),

    # ── Supabase social auth ───────────────────────────────────────────────────
    # <provider> can be: google, github, facebook, twitter, discord, apple, etc.
    path("social/<str:provider>/", views.social_login,    name="social_login"),
    path("callback/",              views.social_callback,  name="social_callback"),

    # ── Account pages ──────────────────────────────────────────────────────────
    path("profile/",        views.profile_view,         name="profile"),
    path("orders/",         views.order_history_view,   name="order_history"),
    path("debug-email/",    views.debug_email_view,     name="debug_email"),
]
