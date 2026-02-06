from services.branding_service import BrandingService

def inject_site_settings():
    """
    Context processor to inject site settings (branding, SEO) into all templates.
    """
    return dict(site_settings=BrandingService.get_active_theme())

def register_context_processors(app):
    """
    Registers context processors on the Flask app.
    """
    app.context_processor(inject_site_settings)
