import stripe
import logging
import json
import csv
from collections import defaultdict
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from .models import SubscriptionPlan, UserSubscription
from django.utils import timezone
from datetime import datetime

# Configure logger
logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def pricing_view(request):
    if request.user.is_staff:
        return redirect('subscriptions:admin_plans')
    from django.http import HttpResponseRedirect
    return HttpResponseRedirect('/accounts/profile/?tab=billing')


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
    user_sub, created = UserSubscription.objects.get_or_create(user=request.user)
    if not user_sub.stripe_customer_id:
        if request.user.is_staff:
            return redirect('subscriptions:admin_plans')
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect('/accounts/profile/?tab=billing')
        
    try:
        portal_session = stripe.billing_portal.Session.create(
            customer=user_sub.stripe_customer_id,
            return_url=request.build_absolute_uri('/accounts/profile/'),
        )
        return redirect(portal_session.url, code=303)
    except Exception as e:
        logger.error(f"Error creating portal session: {e}")
        return render(request, 'subscriptions/error.html', {'error': str(e)})

@staff_member_required
def admin_subscription_metrics(request):
    # Seeding Helper: Populate mock subscriptions across existing users if seed=true
    if request.GET.get('seed') == 'true':
        from django.contrib.auth import get_user_model
        import random
        from datetime import timedelta
        
        User = get_user_model()
        users = User.objects.all()
        plans = SubscriptionPlan.objects.all()
        
        statuses = ['active', 'active', 'active', 'canceled', 'trialing', 'expired']
        
        for u in users:
            plan = random.choice(plans) if plans.exists() else None
            status = random.choice(statuses)
            
            now_dt = timezone.now()
            if status in ['active', 'trialing']:
                start_dt = now_dt - timedelta(days=random.randint(1, 20))
                end_dt = now_dt + timedelta(days=random.randint(5, 30))
            elif status == 'canceled':
                start_dt = now_dt - timedelta(days=random.randint(15, 25))
                end_dt = now_dt + timedelta(days=random.randint(1, 10))
            else: # expired
                start_dt = now_dt - timedelta(days=random.randint(40, 60))
                end_dt = now_dt - timedelta(days=random.randint(10, 30))
                
            user_sub, created = UserSubscription.objects.get_or_create(user=u)
            user_sub.plan = plan
            user_sub.status = status
            user_sub.current_period_start = start_dt
            user_sub.current_period_end = end_dt
            user_sub.stripe_customer_id = f"cus_mock_{u.id}_{random.randint(1000, 9999)}"
            user_sub.stripe_subscription_id = f"sub_mock_{u.id}_{random.randint(1000, 9999)}"
            user_sub.cancel_at_period_end = (status == 'canceled')
            user_sub.save()
            
        return redirect('subscriptions:admin_metrics')

    # Get search & filters parameters
    q = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()
    plan_filter = request.GET.get('plan', '').strip()

    # Query all users subscriptions
    queryset = UserSubscription.objects.select_related('user', 'plan').all()

    # Apply search filter
    if q:
        queryset = queryset.filter(Q(user__username__icontains=q) | Q(user__email__icontains=q))

    # Apply status filter
    if status_filter:
        queryset = queryset.filter(status=status_filter)

    # Apply plan filter
    if plan_filter:
        queryset = queryset.filter(plan_id=plan_filter)

    # CSV Export handling
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="subscribers_export.csv"'
        writer = csv.writer(response)
        writer.writerow(['Username', 'Email', 'Plan Name', 'Price', 'Interval', 'Status', 'Current Period Start', 'Current Period End', 'Created At'])
        for sub in queryset:
            writer.writerow([
                sub.user.username,
                sub.user.email,
                sub.plan.name if sub.plan else 'N/A',
                sub.plan.price if sub.plan else 0,
                sub.plan.get_interval_display() if sub.plan else 'N/A',
                sub.get_status_display(),
                sub.current_period_start.strftime('%Y-%m-%d %H:%M:%S') if sub.current_period_start else 'N/A',
                sub.current_period_end.strftime('%Y-%m-%d %H:%M:%S') if sub.current_period_end else 'N/A',
                sub.created_at.strftime('%Y-%m-%d %H:%M:%S')
            ])
        return response

    # 1. Local Metrics Calculations
    now = timezone.now()
    active_subs = UserSubscription.objects.filter(
        status__in=['active', 'trialing']
    ).filter(
        Q(current_period_end__isnull=True) | Q(current_period_end__gt=now)
    ).select_related('plan')

    active_subscribers_count = active_subs.count()

    mrr = 0
    for sub in active_subs:
        if sub.plan:
            if sub.plan.interval == 'month':
                mrr += sub.plan.price
            elif sub.plan.interval == 'year':
                mrr += sub.plan.price / 12

    arr = mrr * 12
    arpu = mrr / active_subscribers_count if active_subscribers_count > 0 else 0
    total_subscribers_count = UserSubscription.objects.count()

    # 2. Query Stripe Balance Live
    stripe_balance = None
    try:
        stripe.api_key = settings.STRIPE_SECRET_KEY
        balance_resp = stripe.Balance.retrieve()
        
        available_amount = 0
        pending_amount = 0
        currency = 'USD'
        
        for b in balance_resp.get('available', []):
            available_amount += b.get('amount', 0)
            currency = b.get('currency', 'usd').upper()
            
        for b in balance_resp.get('pending', []):
            pending_amount += b.get('amount', 0)
            
        stripe_balance = {
            'available': available_amount / 100.0,
            'pending': pending_amount / 100.0,
            'currency': currency
        }
    except Exception as e:
        logger.error(f"Error retrieving Stripe balance: {e}")

    # 3. Chart Data Calculations
    # Plan Distribution (active only)
    plan_counts = {}
    for sub in active_subs:
        if sub.plan:
            plan_counts[sub.plan.name] = plan_counts.get(sub.plan.name, 0) + 1
            
    # Status Distribution
    status_counts = {}
    for sub in UserSubscription.objects.all():
        status_counts[sub.status] = status_counts.get(sub.status, 0) + 1

    # Growth Timeline (by month)
    import datetime
    timeline_grouped = defaultdict(int)
    for sub in UserSubscription.objects.all():
        key = (sub.created_at.year, sub.created_at.month)
        timeline_grouped[key] += 1
        
    sorted_keys = sorted(timeline_grouped.keys())
    chart_timeline_labels = []
    chart_timeline_values = []
    
    for key in sorted_keys:
        dt = datetime.date(key[0], key[1], 1)
        chart_timeline_labels.append(dt.strftime('%b %Y'))
        chart_timeline_values.append(timeline_grouped[key])

    # Convert to JSON for JS usage
    chart_plan_labels_js = json.dumps(list(plan_counts.keys()))
    chart_plan_values_js = json.dumps(list(plan_counts.values()))
    chart_status_labels_js = json.dumps([s.capitalize() for s in status_counts.keys()])
    chart_status_values_js = json.dumps(list(status_counts.values()))
    chart_timeline_labels_js = json.dumps(chart_timeline_labels)
    chart_timeline_values_js = json.dumps(chart_timeline_values)

    plans = SubscriptionPlan.objects.all()
    statuses = UserSubscription.STATUS_CHOICES

    context = {
        'subscribers': queryset,
        'plans': plans,
        'statuses': statuses,
        'active_subscribers_count': active_subscribers_count,
        'total_subscribers_count': total_subscribers_count,
        'mrr': mrr,
        'arr': arr,
        'arpu': arpu,
        'stripe_balance': stripe_balance,
        'q': q,
        'status_filter': status_filter,
        'plan_filter': plan_filter,
        'chart_plan_labels_js': chart_plan_labels_js,
        'chart_plan_values_js': chart_plan_values_js,
        'chart_status_labels_js': chart_status_labels_js,
        'chart_status_values_js': chart_status_values_js,
        'chart_timeline_labels_js': chart_timeline_labels_js,
        'chart_timeline_values_js': chart_timeline_values_js,
    }

    return render(request, 'subscriptions/admin_metrics.html', context)

@staff_member_required
def admin_subscription_plans(request):
    plans = SubscriptionPlan.objects.all().order_by('price')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create':
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            stripe_price_id = request.POST.get('stripe_price_id')
            price = request.POST.get('price')
            currency = request.POST.get('currency', 'USD')
            interval = request.POST.get('interval', 'month')
            
            if name and stripe_price_id and price:
                SubscriptionPlan.objects.create(
                    name=name,
                    description=description,
                    stripe_price_id=stripe_price_id,
                    price=price,
                    currency=currency,
                    interval=interval,
                    is_active=True
                )
                messages = {'success': f'Plan "{name}" created successfully'}
            else:
                messages = {'error': 'Please fill in all required fields'}
                
        elif action == 'toggle_active':
            plan_id = request.POST.get('plan_id')
            plan = get_object_or_404(SubscriptionPlan, id=plan_id)
            plan.is_active = not plan.is_active
            plan.save()
            messages = {'success': f'Plan "{plan.name}" {"activated" if plan.is_active else "deactivated"}'}
        
        return render(request, 'subscriptions/admin_plans.html', {
            'plans': plans,
            'messages': messages
        })
    
    return render(request, 'subscriptions/admin_plans.html', {'plans': plans, 'messages': None})


@staff_member_required
def admin_edit_plan(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    if request.method == 'POST':
        plan.name = request.POST.get('name', plan.name)
        plan.description = request.POST.get('description', plan.description)
        plan.stripe_price_id = request.POST.get('stripe_price_id', plan.stripe_price_id)
        plan.price = request.POST.get('price', plan.price)
        plan.currency = request.POST.get('currency', plan.currency)
        plan.interval = request.POST.get('interval', plan.interval)
        plan.is_active = request.POST.get('is_active') == 'on'
        plan.save()
        return redirect('subscriptions:admin_plans')
    
    return render(request, 'subscriptions/admin_plan_edit.html', {'plan': plan})


@staff_member_required
def admin_delete_plan(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    
    if request.method == 'POST':
        plan.delete()
        return redirect('subscriptions:admin_plans')
    
    return render(request, 'subscriptions/admin_plan_delete.html', {'plan': plan})

