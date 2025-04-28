def analyze_portfolio(returns: list) -> str:
    """Analyze simple portfolio returns."""
    average_return = sum(returns) / len(returns) if returns else 0
    if average_return > 0:
        return f"📈 Your portfolio is performing well with an average return of {average_return:.2f}%."
    else:
        return f"📉 Your portfolio is underperforming with an average return of {average_return:.2f}%."