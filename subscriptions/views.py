import stripe
import logging
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import SubscriptionPlan, UserSubscription
from django.utils import timezone
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

def pricing_view(request):
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('price')
    return render(request, 'subscriptions/pricing.html', {'plans': plans})

@login_required
def create_checkout_session(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    user_sub, created = UserSubscription.objects.get_or_create(user=request.user)
    
    try:
        checkout_session = stripe.checkout.Session.create(
            customer=user_sub.stripe_customer_id if user_sub.stripe_customer_id else None,
            customer_email=request.user.email if not user_sub.stripe_customer_id else None,
            payment_method_types=['card'],
            line_items=[
                {
                    'price': plan.stripe_price_id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=request.build_absolute_uri('/subscriptions/success/') + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri('/subscriptions/cancel/'),
            metadata={
                'user_id': request.user.id,
                'plan_id': plan.id,
            }
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        logger.error(f"Error creating checkout session: {e}")
        return render(request, 'subscriptions/error.html', {'error': str(e)})

@login_required
def checkout_success(request):
    return render(request, 'subscriptions/success.html')

@login_required
def checkout_cancel(request):
    return render(request, 'subscriptions/cancel.html')

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    if not endpoint_secret:
        logger.error("STRIPE_WEBHOOK_SECRET not set in settings.")
        return HttpResponse(status=400)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        logger.error(f"Invalid payload for webhook: {e}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature for webhook: {e}")
        return HttpResponse(status=400)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        handle_checkout_session(session)
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_updated(subscription)
    elif event['type'] == 'customer.subscription.deleted':
        subscription = event['data']['object']
        handle_subscription_deleted(subscription)

    return HttpResponse(status=200)

def handle_checkout_session(session):
    user_id = session.get('metadata', {}).get('user_id')
    plan_id = session.get('metadata', {}).get('plan_id')
    stripe_customer_id = session.get('customer')
    stripe_subscription_id = session.get('subscription')
    
    if user_id:
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user = User.objects.get(id=user_id)
            user_sub, created = UserSubscription.objects.get_or_create(user=user)
            
            user_sub.stripe_customer_id = stripe_customer_id
            user_sub.stripe_subscription_id = stripe_subscription_id
            if plan_id:
                user_sub.plan_id = plan_id
            
            # Get subscription details from Stripe
            stripe_sub = stripe.Subscription.retrieve(stripe_subscription_id)
            user_sub.status = stripe_sub.status
            user_sub.current_period_start = timezone.make_aware(datetime.fromtimestamp(stripe_sub.current_period_start))
            user_sub.current_period_end = timezone.make_aware(datetime.fromtimestamp(stripe_sub.current_period_end))
            user_sub.save()
            logger.info(f"Subscription updated for user {user_id}")
        except Exception as e:
            logger.error(f"Error handling checkout session: {e}")

def handle_subscription_updated(subscription):
    stripe_subscription_id = subscription.get('id')
    try:
        user_sub = UserSubscription.objects.get(stripe_subscription_id=stripe_subscription_id)
        user_sub.status = subscription.get('status')
        user_sub.current_period_start = timezone.make_aware(datetime.fromtimestamp(subscription.get('current_period_start')))
        user_sub.current_period_end = timezone.make_aware(datetime.fromtimestamp(subscription.get('current_period_end')))
        user_sub.cancel_at_period_end = subscription.get('cancel_at_period_end')
        user_sub.save()
        logger.info(f"Subscription updated: {stripe_subscription_id}")
    except UserSubscription.DoesNotExist:
        logger.warning(f"Subscription updated but user not found: {stripe_subscription_id}")
    except Exception as e:
        logger.error(f"Error handling subscription updated: {e}")

def handle_subscription_deleted(subscription):
    stripe_subscription_id = subscription.get('id')
    try:
        user_sub = UserSubscription.objects.get(stripe_subscription_id=stripe_subscription_id)
        user_sub.status = 'expired'
        user_sub.save()
        logger.info(f"Subscription deleted: {stripe_subscription_id}")
    except UserSubscription.DoesNotExist:
        pass
    except Exception as e:
        logger.error(f"Error handling subscription deleted: {e}")

@login_required
def create_portal_session(request):
    user_sub = get_object_or_404(UserSubscription, user=request.user)
    if not user_sub.stripe_customer_id:
        return redirect('subscriptions:pricing')
        
    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=user_sub.stripe_customer_id,
            return_url=request.build_absolute_uri('/accounts/profile/'),
        )
        return redirect(portal_session.url, code=303)
    except Exception as e:
        logger.error(f"Error creating portal session: {e}")
        return render(request, 'subscriptions/error.html', {'error': str(e)})
