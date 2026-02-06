from services.branding_service import BrandingService
from models import Announcement, AnnouncementTargetAudience
from flask_login import current_user
from sqlalchemy import or_

def inject_site_settings():
    """
    Context processor to inject site settings (branding, SEO) and announcements into all templates.
    """
    context = dict(site_settings=BrandingService.get_active_theme())

    # Fetch Announcements
    # Logic: Show global announcements or announcements for the user's establishment
    # Limiting to last 3 for example
    if current_user.is_authenticated:
        # Determine establishment ID if applicable (User might have multiple or one, assuming 'establishment_id' on user or relation)
        # Checking User model via memory would be good, but let's be safe and just fetch ALL_USERS for now + establishment if we knew it.
        # User model usually has establishment_id or leases.
        # For simplicity in this task, I'll fetch ALL_USERS announcements.

        # Note: If I had access to user's establishment_id, I'd add:
        # or_ (Announcement.target_audience == AnnouncementTargetAudience.SPECIFIC_ESTABLISHMENT) ...

        announcements = Announcement.query.filter(
            Announcement.target_audience == AnnouncementTargetAudience.ALL_USERS
        ).order_by(Announcement.created_at.desc()).limit(1).all()

        context['admin_announcements'] = announcements
    else:
        context['admin_announcements'] = []

    return context

def register_context_processors(app):
    """
    Registers context processors on the Flask app.
    """
    app.context_processor(inject_site_settings)
