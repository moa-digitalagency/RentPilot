from models.saas_config import PlatformSettings
import json

class BrandingService:
    DEFAULT_THEME = {
        'primary_color': '#4F46E5', # Indigo-600
        'secondary_color': '#8B5CF6', # Violet-500
        'logo_url': '/statics/img/logo_default.png', # Placeholder default
        'app_name': 'RentPilot',
        'whatsapp_contact_number': None,
        'footer_text': None,
        'copyright_text': None,
        'social_media_config': {},
        'footer_links': [],
        'landing_hero_background_url': None,
        # SEO
        'seo_title_template': '%s | RentPilot',
        'seo_meta_desc': 'SaaS de gestion locative moderne.',
        'is_maintenance_mode': False,
        'receipt_format': 'A4_Standard'
    }

    @staticmethod
    def get_active_theme():
        """
        Retrieves the active branding theme from the database.
        Returns a dictionary mimicking the PlatformSettings object structure for template compatibility.
        """
        try:
            settings = PlatformSettings.query.first()
            if settings:
                return {
                    'primary_color': settings.primary_color_hex or BrandingService.DEFAULT_THEME['primary_color'],
                    'secondary_color': settings.secondary_color_hex or BrandingService.DEFAULT_THEME['secondary_color'],
                    'logo_url': settings.logo_url or BrandingService.DEFAULT_THEME['logo_url'],
                    'app_name': settings.app_name or BrandingService.DEFAULT_THEME['app_name'],
                    'whatsapp_contact_number': settings.whatsapp_contact_number,

                    # New V4 Fields
                    'footer_text': settings.footer_text,
                    'copyright_text': settings.copyright_text,
                    'social_media_config': settings.social_media_config or {},
                    'footer_links': settings.footer_links or [],
                    'landing_hero_background_url': settings.landing_hero_background_url,

                    # Existing but missed
                    'seo_title_template': settings.seo_title_template,
                    'seo_meta_desc': settings.seo_meta_desc,
                    'is_maintenance_mode': settings.is_maintenance_mode,
                    'receipt_format': settings.receipt_format
                }
        except Exception as e:
            # Fallback in case of DB error or context issues
            print(f"Error fetching branding settings: {e}")
            pass

        return BrandingService.DEFAULT_THEME
