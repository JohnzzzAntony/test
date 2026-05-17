"""
accounts/views.py  ← REPLACE your existing file
=================================================
All original views preserved and improved.
Google OAuth removed completely.
Supabase social auth fully wired up with welcome e-mail support.

Supported Supabase providers (enable each in Supabase Dashboard):
  google, github, facebook, twitter, discord, apple, linkedin, spotify
"""

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django_ratelimit.decorators import ratelimit


from .forms import CustomUserCreationForm
from .email_notifications import send_welcome_email, send_login_alert, test_email_connection

logger = logging.getLogger(__name__)


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _get_supabase():
    """Return the Supabase client or None, with a user-facing error on failure."""
    from core.supabase_client import supabase
    return supabase


def _get_or_create_user(email: str, full_name: str = "", provider: str = ""):
    """
    Find an existing Django user by e-mail or create a new one.
    OAuth users get an unusable password — they can only log in via Supabase.
    Returns (user, created).
    """
    email = email.lower().strip()
    first_name = ""
    last_name  = ""

    if full_name:
        parts      = full_name.strip().split(" ", 1)
        first_name = parts[0]
        last_name  = parts[1] if len(parts) > 1 else ""

    try:
        user = User.objects.get(email__iexact=email)
        # Keep names in sync if they were empty before
        changed = False
        if first_name and not user.first_name:
            user.first_name = first_name
            changed = True
        if last_name and not user.last_name:
            user.last_name = last_name
            changed = True
        if changed:
            user.save(update_fields=["first_name", "last_name"])
        return user, False

    except User.DoesNotExist:
        base_username = email.split("@")[0]
        username      = base_username
        counter       = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_unusable_password()
        user.save()
        logger.info("New user created via %s: %s", provider, email)
        return user, True


# ─── Standard Registration ────────────────────────────────────────────────────

@ratelimit(key="ip", rate="5/m", method="POST", block=True)
def register_view(request):
    """Standard username + password registration with welcome e-mail."""
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            send_welcome_email(user)           # ← welcome e-mail
            messages.success(
                request,
                f"Welcome {user.username}! Your account has been created."
            )
            return redirect("core:home")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.replace('_', ' ').capitalize()}: {error}")
    else:
        form = CustomUserCreationForm()

    return render(request, "accounts/register.html", {"form": form})


# ─── Standard Login / Logout ──────────────────────────────────────────────────

@ratelimit(key="ip", rate="5/m", method="POST", block=True)
def login_view(request):
    """Standard username + password login."""
    if request.user.is_authenticated:
        return redirect("core:home")

    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome back, {user.first_name or username}!")
                next_url = request.GET.get("next")
                return redirect(next_url if next_url else "core:home")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = AuthenticationForm()

    next_url = request.GET.get("next")
    return render(request, "accounts/login.html", {"form": form, "next": next_url})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("core:home")


# ─── Guest Checkout ───────────────────────────────────────────────────────────

def guest_checkout_view(request):
    """Allow checkout without an account."""
    next_url = request.GET.get("next", "orders:checkout")
    if request.user.is_authenticated:
        return redirect(next_url)
    request.session["is_guest_checkout"] = True
    return redirect(next_url)


# ─── Supabase Social Auth ─────────────────────────────────────────────────────

def social_login(request, provider):
    """
    Step 1 — Redirect the user to the chosen social provider via Supabase.

    Supported provider slugs (must also be enabled in Supabase Dashboard):
        google, github, facebook, twitter, discord, apple, linkedin, spotify

    Usage in templates:
        <a href="{% url 'accounts:social_login' 'google' %}">Google</a>
        <a href="{% url 'accounts:social_login' 'github' %}">GitHub</a>
    """
    SUPPORTED_PROVIDERS = {
        "github", "facebook", "twitter",
        "discord", "apple", "linkedin", "spotify",
    }

    provider = provider.lower().strip()
    if provider not in SUPPORTED_PROVIDERS:
        messages.error(request, f"'{provider}' is not a supported login provider.")
        return redirect("accounts:login")

    supabase = _get_supabase()
    if not supabase:
        messages.error(
            request,
            "Social login is temporarily unavailable. Please use email & password."
        )
        return redirect("accounts:login")

    try:
        # The callback URL must match what is set in:
        #   Supabase Dashboard → Authentication → URL Configuration → Redirect URLs
        redirect_to = request.build_absolute_uri("/accounts/callback/")

        result = supabase.auth.sign_in_with_oauth({
            "provider": provider,
            "options": {
                "redirect_to": redirect_to,
                "scopes": "email profile",   # request email + profile from provider
            },
        })

        if hasattr(result, "url") and result.url:
            # Store provider in session so the callback knows which one was used
            request.session["oauth_provider"] = provider
            return redirect(result.url)

        messages.error(request, "Could not generate a login URL. Please try again.")
        return redirect("accounts:login")

    except Exception as exc:
        logger.error("social_login error (%s): %s", provider, exc)
        messages.error(
            request,
            "Social login is currently unavailable. Please use email & password."
        )
        return redirect("accounts:login")


def social_callback(request):
    """
    Step 2 — Supabase redirects here after the user approves the social login.

    Flow:
      1. Supabase appends an access_token fragment to the redirect URL.
      2. A small JS snippet (included in base.html) picks up the token from
         the URL hash and POSTs it to this view as a hidden form field.
      3. We call supabase.auth.get_user(token) to verify and fetch the profile.
      4. We create or retrieve the matching Django User and log them in.
    """
    supabase = _get_supabase()
    if not supabase:
        messages.error(request, "Authentication failed. Please use email & password.")
        return redirect("accounts:login")

    # ── Token extraction ───────────────────────────────────────────────────────
    # The access token is sent either as a POST field (from the JS helper) or
    # as a GET query parameter (some providers / older Supabase versions).
    access_token = (
        request.POST.get("access_token")
        or request.GET.get("access_token")
        or ""
    ).strip()

    # If no token yet, render the JS-helper page that grabs it from the URL hash
    if not access_token:
        return render(request, "accounts/oauth_callback.html")

    # ── Verify token with Supabase ─────────────────────────────────────────────
    try:
        res = supabase.auth.get_user(access_token)
        if not res or not res.user:
            raise ValueError("No user returned from Supabase.")

        supabase_user = res.user
        email         = (supabase_user.email or "").lower().strip()

        if not email:
            raise ValueError("No e-mail address returned from social provider.")

        # Pull display name from user_metadata (varies by provider)
        meta      = supabase_user.user_metadata or {}
        full_name = (
            meta.get("full_name")
            or meta.get("name")
            or meta.get("user_name")
            or email.split("@")[0]
        )

        provider = (
            request.session.pop("oauth_provider", None)
            or (supabase_user.app_metadata or {}).get("provider", "Social")
        )

        # ── Sync with Django User ──────────────────────────────────────────────
        user, created = _get_or_create_user(
            email=email,
            full_name=full_name,
            provider=provider,
        )

        if created:
            send_welcome_email(user)   # ← welcome e-mail for brand-new accounts

        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(
            request,
            f"Welcome{' back' if not created else ''}, "
            f"{user.first_name or user.username}! "
            f"(Signed in via {provider.capitalize()})"
        )
        return redirect("core:home")

    except Exception as exc:
        logger.error("social_callback error: %s", exc)
        messages.error(
            request,
            "Authentication failed. Please try again or use email & password."
        )
        return redirect("accounts:login")


# ─── Profile & Order History ──────────────────────────────────────────────────

@login_required
def profile_view(request):
    """User profile dashboard."""
    from orders.models import CustomerOrder
    from products.models import Wishlist

    orders         = CustomerOrder.objects.filter(user=request.user).order_by("-created_at")[:5]
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    total_orders   = CustomerOrder.objects.filter(user=request.user).count()

    return render(request, "accounts/profile.html", {
        "orders":        orders,
        "wishlist_count": wishlist_count,
        "total_orders":  total_orders,
    })


@login_required
def order_history_view(request):
    """Full order history for the logged-in user."""
    from orders.models import CustomerOrder
    orders = CustomerOrder.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "accounts/order_history.html", {"orders": orders})


@login_required
def debug_email_view(request):
    """Admin-only view to test e-mail sending and view configuration."""
    if not request.user.is_superuser:
        messages.error(request, "Access denied. Admin only.")
        return redirect("core:home")

    status_msg = ""
    if request.GET.get("send") == "1":
        # Trigger the test e-mail
        status_msg = test_email_connection(to_email=request.user.email)
        messages.success(request, f"Test email triggered! Sent to {request.user.email}")

    # Check settings
    from django.conf import settings
    email_config = {
        "EMAIL_BACKEND": settings.EMAIL_BACKEND,
        "EMAIL_HOST": settings.EMAIL_HOST,
        "EMAIL_PORT": settings.EMAIL_PORT,
        "EMAIL_USE_TLS": settings.EMAIL_USE_TLS,
        "EMAIL_HOST_USER": settings.EMAIL_HOST_USER,
        "DEFAULT_FROM_EMAIL": settings.DEFAULT_FROM_EMAIL,
    }

    return render(request, "accounts/debug_email.html", {
        "email_config": email_config,
        "status_msg": status_msg,
    })
