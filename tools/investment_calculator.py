def calculate_investment_return(initial_amount: float, final_amount: float) -> float:
    """Calculate simple investment return in %."""
    if initial_amount == 0:
        return 0.0
    return ((final_amount - initial_amount) / initial_amount) * 100