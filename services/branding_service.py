from models.saas_config import PlatformSettings

class BrandingService:
    DEFAULT_THEME = {
        'primary_color': '#4F46E5', # Indigo-600
        'secondary_color': '#8B5CF6', # Violet-500
        'logo_url': '/statics/img/logo_default.png', # Placeholder default
        'app_name': 'RentPilot'
    }

    @staticmethod
    def get_active_theme():
        """
        Retrieves the active branding theme from the database.
        Returns a dictionary with primary_color, secondary_color, logo_url, and app_name.
        """
        try:
            settings = PlatformSettings.query.first()
            if settings:
                return {
                    'primary_color': settings.primary_color_hex or BrandingService.DEFAULT_THEME['primary_color'],
                    'secondary_color': settings.secondary_color_hex or BrandingService.DEFAULT_THEME['secondary_color'],
                    'logo_url': settings.logo_url or BrandingService.DEFAULT_THEME['logo_url'],
                    'app_name': settings.app_name or BrandingService.DEFAULT_THEME['app_name']
                }
        except Exception as e:
            # Fallback in case of DB error or context issues
            print(f"Error fetching branding settings: {e}")
            pass

        return BrandingService.DEFAULT_THEME
