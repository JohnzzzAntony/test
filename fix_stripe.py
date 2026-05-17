import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jkr.settings')
django.setup()

import stripe
from django.conf import settings
from subscriptions.models import SubscriptionPlan

stripe.api_key = settings.STRIPE_SECRET_KEY

print("Starting to fix Stripe prices...")
for plan in SubscriptionPlan.objects.all():
    print(f"Processing plan: {plan.name} - current price id: {plan.stripe_price_id}")
    try:
        if plan.stripe_price_id and not ("Monthly" in plan.stripe_price_id or "Yearly" in plan.stripe_price_id):
            stripe.Price.retrieve(plan.stripe_price_id)
            print(f"  Valid Stripe Price ID: {plan.stripe_price_id}")
            continue
        else:
            raise stripe.error.InvalidRequestError("Force invalid for dummy IDs", "id")
    except stripe.error.InvalidRequestError:
        print(f"  Invalid or dummy Stripe Price ID. Creating new in Stripe...")
        
        # Create Product
        product = stripe.Product.create(
            name=plan.name,
            description=plan.description or f"{plan.name} Plan"
        )
        
        # Create Price
        price = stripe.Price.create(
            product=product.id,
            unit_amount=int(plan.price * 100),
            currency=plan.currency.lower(),
            recurring={"interval": plan.interval},
        )
        
        # Update DB
        plan.stripe_price_id = price.id
        plan.save()
        print(f"  -> Created new Stripe Price: {price.id} for {plan.name} (DB Updated)")

print("Done fixing prices!")
