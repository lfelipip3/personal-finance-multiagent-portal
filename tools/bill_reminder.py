def remind_upcoming_bills(bills: list) -> str:
    """Simple reminder for bills."""
    if not bills:
        return "You have no upcoming bills!"
    
    message = "📋 Upcoming Bills:\n"
    for bill in bills:
        message += f"- {bill['name']} due on {bill['due_date']}\n"
    return message