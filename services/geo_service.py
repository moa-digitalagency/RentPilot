
"""
* Nom de l'application : RentPilot
* Description : Service for Geolocation using APILayer.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
import requests
import os
from flask import current_app

class GeoService:
    BASE_URL = "https://api.apilayer.com/geo/city/search"
    # Note: The exact URL structure depends on the specific API from APILayer (there are many).
    # Assuming standard "Geo API" search.
    # If the user meant 'ipstack' or similar on APILayer, the endpoint might differ.
    # Based on "marketplace.apilayer.com/geo-api", it's likely the Geo API.

    @staticmethod
    def get_api_key():
        return current_app.config.get('GEO_API_KEY') or os.environ.get('GEO_API_KEY')

    @staticmethod
    def search_city(query):
        """
        Search for a city by name.
        Returns a list of dicts with 'city', 'country', 'country_code'.
        """
        api_key = GeoService.get_api_key()
        if not api_key:
            # Fallback / Mock for development without key
            return GeoService._mock_search(query)

        headers = {
            "apikey": api_key
        }
        params = {
            "city": query
        }

        try:
            response = requests.get(GeoService.BASE_URL, headers=headers, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                # Adapt response format based on actual API return
                # Assuming generic list of cities
                results = []
                # Check format (usually data is a list or inside a key)
                # This is a best-guess implementation without live API docs access in sandbox
                if isinstance(data, list):
                    items = data
                else:
                    items = data.get('data', []) or data.get('results', [])

                for item in items:
                    results.append({
                        'city': item.get('name', item.get('city')),
                        'country': item.get('country', {}).get('name') if isinstance(item.get('country'), dict) else item.get('country'),
                        'country_code': item.get('country_code', 'XX')
                    })
                return results
            else:
                print(f"GeoAPI Error: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"GeoAPI Exception: {e}")
            return []

    @staticmethod
    def _mock_search(query):
        """
        Mock data for development.
        """
        query = query.lower()
        mock_db = [
            {'city': 'Paris', 'country': 'France', 'country_code': 'FR'},
            {'city': 'Lyon', 'country': 'France', 'country_code': 'FR'},
            {'city': 'Marseille', 'country': 'France', 'country_code': 'FR'},
            {'city': 'Brussels', 'country': 'Belgium', 'country_code': 'BE'},
            {'city': 'London', 'country': 'United Kingdom', 'country_code': 'GB'},
            {'city': 'Madrid', 'country': 'Spain', 'country_code': 'ES'},
            {'city': 'Barcelona', 'country': 'Spain', 'country_code': 'ES'},
            {'city': 'Berlin', 'country': 'Germany', 'country_code': 'DE'},
            {'city': 'New York', 'country': 'United States', 'country_code': 'US'},
        ]
        return [c for c in mock_db if query in c['city'].lower()]

    @staticmethod
    def get_client_ip_info(ip_address):
        """
        Get location info from IP address.
        Uses a free service or APILayer's IP to Location if available.
        """
        # For this demo, we can use a free public API like ipapi.co
        # In production, use the paid APILayer key if it supports IP lookup.
        try:
            response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=3)
            if response.status_code == 200:
                data = response.json()
                return {
                    'city': data.get('city'),
                    'country': data.get('country_name'),
                    'country_code': data.get('country_code')
                }
        except:
            pass
        return None
