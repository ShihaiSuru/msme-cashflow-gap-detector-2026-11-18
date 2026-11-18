#!/usr/bin/env python3
"""
MSME Cash Flow Gap Detector
Starter demo for Indian MSMEs: analyzes sample GST invoices and bank inflows
to detect cash-flow gaps and estimate working capital needs.

No external dependencies required for the core demo (pure Python).
Extend with pandas, openpyxl, or ML libraries for production use.
"""

from datetime import datetime, timedelta
from collections import defaultdict

# ---------------------------------------------------------------------------
# Sample data — typical MSME scenario (amounts in INR)
# ---------------------------------------------------------------------------

# Outstanding GST invoices (receivables)
INVOICES = [
    {"invoice_id": "INV-001", "customer": "Buyer A (Retailer)", "amount": 250000, "due_date": "2026-11-25", "status": "pending"},
    {"invoice_id": "INV-002", "customer": "Buyer B (Distributor)", "amount": 180000, "due_date": "2026-12-05", "status": "pending"},
    {"invoice_id": "INV-003", "customer": "Buyer C (OEM)", "amount": 420000, "due_date": "2026-11-20", "status": "overdue"},
    {"invoice_id": "INV-004", "customer": "Buyer A (Retailer)", "amount": 95000, "due_date": "2026-12-15", "status": "pending"},
]

# Expected bank inflows (from previous patterns / UPI / NEFT)
EXPECTED_INFLOWS = [
    {"source": "Buyer A partial", "amount": 120000, "expected_date": "2026-11-22"},
    {"source": "Buyer C overdue collection", "amount": 200000, "expected_date": "2026-11-28"},
    {"source": "New order advance", "amount": 75000, "expected_date": "2026-12-01"},
]

# Fixed monthly operating costs (outflows)
MONTHLY_OUTFLOWS = 280000  # salaries, rent, materials, GST, etc.

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def parse_date(date_str: str) -> datetime:
    """Convert YYYY-MM-DD string to datetime."""
    return datetime.strptime(date_str, "%Y-%m-%d")

def days_from_today(date_str: str) -> int:
    """Days until / since the given date (negative = overdue)."""
    today = datetime(2026, 11, 18)  # fixed demo date matching repo
    return (parse_date(date_str) - today).days

def age_receivables(invoices: list) -> dict:
    """Bucket invoices by aging."""
    buckets = defaultdict(float)
    for inv in invoices:
        days = days_from_today(inv["due_date"])
        if days < 0:
            buckets["Overdue"] += inv["amount"]
        elif days <= 15:
            buckets["0-15 days"] += inv["amount"]
        elif days <= 30:
            buckets["16-30 days"] += inv["amount"]
        else:
            buckets["30+ days"] += inv["amount"]
    return dict(buckets)

def project_cash_position(invoices, inflows, monthly_outflow, horizon_days=45):
    """Simple projection: cumulative expected inflows minus prorated outflows."""
    today = datetime(2026, 11, 18)
    end_date = today + timedelta(days=horizon_days)

    # Collect all expected cash events
    events = []
    for inv in invoices:
        if inv["status"] in ("pending", "overdue"):
            events.append((parse_date(inv["due_date"]), inv["amount"], f"Invoice {inv['invoice_id']}"))
    for inf in inflows:
        events.append((parse_date(inf["expected_date"]), inf["amount"], inf["source"]))

    # Prorate monthly outflow across the horizon
    daily_outflow = monthly_outflow / 30
    total_outflow = daily_outflow * horizon_days

    total_inflow = sum(amt for _, amt, _ in events if parse_date("2026-11-18") <= _ <= end_date)
    net = total_inflow - total_outflow
    return {
        "horizon_days": horizon_days,
        "expected_inflows": total_inflow,
        "expected_outflows": total_outflow,
        "net_position": net,
        "gap": max(0, -net),
    }

# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("MSME CASH-FLOW GAP DETECTOR  |  Demo Date: 18 Nov 2026")
    print("=" * 60)

    # 1. Receivables aging
    print("\n📊 RECEIVABLES AGING (INR)")
    aging = age_receivables(INVOICES)
    for bucket, amount in aging.items():
        print(f"  {bucket:12} : ₹{amount:>10,.0f}")
    total_receivables = sum(aging.values())
    print(f"  {'TOTAL':12} : ₹{total_receivables:>10,.0f}")

    # 2. Cash-flow projection
    print("\n📈 45-DAY CASH-FLOW PROJECTION")
    projection = project_cash_position(INVOICES, EXPECTED_INFLOWS, MONTHLY_OUTFLOWS)
    print(f"  Expected inflows   : ₹{projection['expected_inflows']:>10,.0f}")
    print(f"  Expected outflows  : ₹{projection['expected_outflows']:>10,.0f}")
    print(f"  Net position       : ₹{projection['net_position']:>10,.0f}")

    # 3. Gap detection & working capital estimate
    gap = projection["gap"]
    print("\n⚠️  CASH-FLOW GAP ANALYSIS")
    if gap > 0:
        print(f"  Detected shortfall : ₹{gap:>10,.0f}")
        # Recommend a buffer (e.g., 20% extra for safety)
        recommended_wc = gap * 1.20
        print(f"  Recommended working capital buffer : ₹{recommended_wc:>10,.0f}")
        print("\n  💡 Suggested actions:")
        print("     • Prioritize collection of overdue invoice INV-003")
        print("     • Offer early-payment discount to Buyer A")
        print("     • Explore invoice discounting (TReDS) for large receivables")
        print("     • Review supplier payment terms to free up cash")
    else:
        print("  No cash-flow gap detected in the 45-day horizon.")
        print(f"  Surplus buffer available: ₹{-projection['net_position']:>10,.0f}")

    print("\n" + "=" * 60)
    print("Demo complete. Replace sample data with real GST / bank exports to productionise.")
    print("=" * 60)

if __name__ == "__main__":
    main()
