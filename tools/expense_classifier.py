def classify_expense(description: str) -> str:
    """Simple expense classifier based on keywords."""
    description = description.lower()
    if any(word in description for word in ["uber", "taxi", "flight", "bus", "transport"]):
        return "Transportation"
    elif any(word in description for word in ["grocery", "supermarket", "food", "restaurant"]):
        return "Groceries"
    elif any(word in description for word in ["movie", "cinema", "concert", "netflix"]):
        return "Entertainment"
    elif any(word in description for word in ["electricity", "water", "internet", "utility"]):
        return "Utilities"
    else:
        return "Other"