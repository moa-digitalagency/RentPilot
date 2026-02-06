import random

def fuzz_location(address: str, radius_approx_meters: int = 200) -> str:
    """
    Generates a fuzzy location string or coordinates.
    Since we don't have a real geocoder, we will simulate a fuzzed representation.

    If this were a real app, we would:
    1. Geocode 'address' to (lat, lon).
    2. Add a random offset within 'radius_approx_meters'.
    3. Return the fuzzed (lat, lon) or a generic name (e.g. 'Paris 11ème').

    For now, we return a string indicating it's approximate.
    """
    # Simple simulation of obfuscation
    if not address:
        return "Localisation inconnue"

    parts = address.split(',')
    if len(parts) > 1:
        # Return only the city/zip part if possible
        return f"{parts[-1].strip()} (Approx ~{radius_approx_meters}m)"
    else:
        # Just append a tag
        return f"{address} (Zone approximative)"
