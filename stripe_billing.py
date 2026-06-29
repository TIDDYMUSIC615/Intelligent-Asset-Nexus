import os
import stripe

# Initialize your Stripe production/test key safely from system memory
stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "sk_test_placeholder_key")

# Core Engine Parameters
PERFORMANCE_FEE_PERCENT = 0.15
MILESTONE_INCREMENT = 5000.00

def execute_milestone_billing(user_id: int, stripe_cust_id: str, current_net_profit: float, historical_hwm: float) -> float:
    """
    Sovereign Split Engine: Processes the 15% performance fee billing via Stripe 
    whenever a subscriber crosses a new $5,000 net profit milestone.
    """
    print(f"\n--- [AUDITING PIPELINE] User ID: {user_id} | Cust: {stripe_cust_id} ---")
    
    # Rule 1: If current profit hasn't exceeded the high-water mark, do nothing
    if current_net_profit <= historical_hwm:
        print(f"Stand Down: Current Profit (${current_net_profit:,.2f}) has not broken old HWM (${historical_hwm:,.2f})")
        return historical_hwm
        
    # Rule 2: Compute pure expansion over the historical baseline
    profit_expansion = current_net_profit - historical_hwm
    milestones_crossed = int(profit_expansion // MILESTONE_INCREMENT)
    
    # Rule 3: If profit grew but didn't cleanly cross a full $5,000 threshold, pass
    if milestones_crossed == 0:
        print(f"Baseline Expansion: Up ${profit_expansion:,.2f}, but waiting to clear next ${MILESTONE_INCREMENT:,.2f} milestone block.")
        return historical_hwm
        
    # Calculate exact billable allocations
    total_billable_profit = milestones_crossed * MILESTONE_INCREMENT
    house_fee = total_billable_profit * PERFORMANCE_FEE_PERCENT
    fee_in_cents = int(house_fee * 100) # Stripe processes payments in raw integer cents
    
    # Determine target high-water mark level
    new_hwm = historical_hwm + total_billable_profit
    
    try:
        print(f"🚨 MILESTONE TRIGGERED: {milestones_crossed} target block(s) cleared!")
        print(f"Capturing 15% Split on ${total_billable_profit:,.2f} -> Invoicing: ${house_fee:,.2f}")
        
        # Step A: Queue up the line item details inside the customer's billing profile
        stripe.InvoiceItem.create(
            customer=stripe_cust_id,
            amount=fee_in_cents,
            currency="usd",
            description=f"MND Control Group - Arsenal Performance Fee: 15% Split on ${total_billable_profit:,.2f} profit milestone expansion."
        )
        
        # Step B: Instantly build the final invoice and auto-charge the credit card on file
        invoice = stripe.Invoice.create(
            customer=stripe_cust_id,
            collection_method="charge_automatically",
            auto_advance=True # Finalizes and fires the payment gateway handshake immediately
        )
        
        print(f"✅ STRIPE PIPELINE RECONCILED: Invoice {invoice.id} processed successfully.")
        return new_hwm
        
    except Exception as stripe_err:
        print(f"❌ STRIPE ROUTING BLOCKED: {str(stripe_err)}")
        print("Safety Protocol Engaged: Retaining historical HWM to prevent uncollected database drift.")
        return historical_hwm