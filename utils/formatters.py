from datetime import datetime, timedelta

def format_currency(amount: float) -> str:
    """Formats a float as a currency string (e.g., '1 234,56 €')."""
    try:
        return "{:,.2f}".format(amount).replace(",", "X").replace(".", ",").replace("X", " ") + " €"
    except (ValueError, TypeError):
        return "0,00 €"

def format_date_human(dt: datetime) -> str:
    """Formats a datetime object as a human-readable relative string."""
    if not dt:
        return ""

    now = datetime.utcnow()
    diff = now - dt

    if diff.days > 365:
        return dt.strftime("%d/%m/%Y")
    elif diff.days > 0:
        if diff.days == 1:
            return "hier"
        return f"il y a {diff.days} jours"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"il y a {hours} h"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"il y a {minutes} min"
    else:
        return "à l'instant"
