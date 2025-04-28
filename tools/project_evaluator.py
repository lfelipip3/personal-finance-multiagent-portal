def build_cash_flows(project):
    """Expand structured project info into a cash flow list."""
    periods = project["periods"]
    base_income = project.get("base_income", 0)
    growth_rate = project.get("growth_rate", 0)
    expenses = project.get("expenses", 0)
    unexpected_costs = project.get("unexpected_costs", {})

    cash_flows = []

    for period in range(1, periods + 1):
        # Grow income if growth_rate > 0
        income = base_income * ((1 + growth_rate) ** (period - 1))
        # Calculate basic cash flow
        net_cash_flow = income - expenses
        # Apply unexpected cost if exists
        if str(period) in unexpected_costs:
            net_cash_flow -= unexpected_costs[str(period)]
        cash_flows.append(net_cash_flow)

    return cash_flows

def calculate_project_npv(initial_investment, cash_flows, discount_rate):
    """Calculate the NPV of a project given initial investment and cash flows."""
    npv = -initial_investment
    for t, cash_flow in enumerate(cash_flows, start=1):
        npv += cash_flow / ((1 + discount_rate) ** t)
    return npv