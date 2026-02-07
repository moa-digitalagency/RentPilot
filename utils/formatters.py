
"""
* Nom de l'application : RentPilot
* Description : Source file: formatters.py
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from datetime import datetime, timedelta

def format_currency(amount: float, currency: str = "€") -> str:
    """
    Formats a float as a currency string (e.g., "1 250,50 €").
    """
    try:
        return f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", " ") + f" {currency}"
    except (ValueError, TypeError):
        return f"0,00 {currency}"

def time_since(dt: datetime, default: str = "Just now") -> str:
    """
    Returns a string representing time since the given datetime (e.g., "Il y a 2 min").
    """
    if dt is None:
        return ""

    now = datetime.now()
    diff = now - dt

    seconds = diff.total_seconds()

    if seconds < 0:
        return "Dans le futur"

    if seconds < 60:
        return "À l'instant"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"Il y a {minutes} min"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"Il y a {hours} h"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"Il y a {days} j"
    else:
        return dt.strftime("%d/%m/%Y")