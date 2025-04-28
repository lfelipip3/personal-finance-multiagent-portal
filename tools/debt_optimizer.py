def suggest_debt_payoff(budget: float, monthly_debt_payment: float) -> str:
    """Suggest if extra payments are possible."""
    if budget > monthly_debt_payment * 1.5:
        return "✅ You can consider making extra payments to reduce your debt faster."
    else:
        return "⚠️ Stick to your regular payment schedule for now."