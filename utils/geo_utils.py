
"""
* Nom de l'application : RentPilot
* Description : Source file: geo_utils.py
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import random
import re
from typing import Tuple, Optional

def fuzz_coordinates(lat: float, lon: float, radius_meters: int = 200) -> Tuple[float, float]:
    """
    Adds random noise to coordinates to obscure exact location.
    1 degree latitude ~= 111,000 meters.
    1 degree longitude ~= 111,000 * cos(lat) meters.

    This is a simple approximation.
    """
    if lat is None or lon is None:
        return (0.0, 0.0)

    # Convert radius to degrees (approx)
    # 0.001 degrees is roughly 111 meters
    offset_deg = (radius_meters / 111000.0)

    # Randomize
    delta_lat = random.uniform(-offset_deg, offset_deg)
    delta_lon = random.uniform(-offset_deg, offset_deg)

    return (lat + delta_lat, lon + delta_lon)

def obfuscate_address(address: str) -> str:
    """
    Removes street numbers to give a fuzzy address string.
    Example: "12 Rue de la Paix, 75000 Paris" -> "Rue de la Paix, 75000 Paris"
    """
    if not address:
        return ""

    # Regex to look for starting numbers followed by space/comma
    # Matches "12, " or "12 " at start
    fuzzy = re.sub(r'^\d+\s*,?\s*', '', address)

    # Also handle "12 bis" or similar if needed, keeping it simple for now
    return fuzzy.capitalize()

def generate_fuzzy_location_str(address: str) -> str:
    """
    High-level utility to get the 'Fuzzy Location' string for the database.
    """
    return obfuscate_address(address)