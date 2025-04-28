def check_budget(category_spent: float, category_budget: float) -> str:
    """Check if the user is within budget."""
    if category_spent > category_budget:
        return f"⚠️ You have overspent your budget by ${category_spent - category_budget:.2f}."
    else:
        return f"✅ You are within your budget. You have ${category_budget - category_spent:.2f} remaining."