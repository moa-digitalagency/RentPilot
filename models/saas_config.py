
"""
* Nom de l'application : RentPilot
* Description : Source file: saas_config.py
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from config.extensions import db
from sqlalchemy.sql import func
from sqlalchemy import Enum as SQLAlchemyEnum
from datetime import datetime
import enum

class ReceiptFormat(enum.Enum):
    A4_Standard = 'A4_Standard'
    Thermal_80mm = 'Thermal_80mm'

class PlatformSettings(db.Model):
    """
    Singleton model for platform-wide configuration (White-labeling, SEO).
    """
    __tablename__ = 'platform_settings'

    id = db.Column(db.Integer, primary_key=True)
    app_name = db.Column(db.String(100), default="RentPilot")
    logo_url = db.Column(db.String(255), nullable=True)
    primary_color_hex = db.Column(db.String(7), default="#4F46E5") # Indigo-600
    secondary_color_hex = db.Column(db.String(7), default="#8B5CF6") # Violet-500
    timezone = db.Column(db.String(50), default="UTC")

    # SEO
    seo_title_template = db.Column(db.String(100), default="%s | RentPilot")
    seo_meta_desc = db.Column(db.String(255), default="SaaS de gestion locative moderne.")

    is_maintenance_mode = db.Column(db.Boolean, default=False)

    # New V3 fields
    whatsapp_contact_number = db.Column(db.String(20), nullable=True)
    receipt_format = db.Column(SQLAlchemyEnum(ReceiptFormat), default=ReceiptFormat.A4_Standard, nullable=False)
    receipt_custom_css = db.Column(db.Text, nullable=True)

    # V4: Public Interface Config
    landing_hero_background_url = db.Column(db.String(255), nullable=True)
    footer_text = db.Column(db.Text, nullable=True)
    copyright_text = db.Column(db.String(255), nullable=True)

    # JSON Configs for flexible social media and links
    # Structure: {"facebook": "url", "twitter": "url", "instagram": "url", "linkedin": "url"}
    social_media_config = db.Column(db.JSON, nullable=True)

    # Structure: [{"label": "Privacy", "url": "/privacy"}, ...]
    footer_links = db.Column(db.JSON, nullable=True)

    # PWA Configuration
    pwa_enabled = db.Column(db.Boolean, default=False)
    pwa_display_mode = db.Column(db.String(20), default="default") # 'default' or 'custom'
    pwa_custom_name = db.Column(db.String(100), nullable=True)
    pwa_custom_icon_url = db.Column(db.String(255), nullable=True)

    def save(self):
        if not self.id:
            # Ensure singleton
            existing = PlatformSettings.query.first()
            if existing:
                self.id = existing.id
        db.session.add(self)
        db.session.commit()

class SubscriptionPlan(db.Model):
    """
    SaaS Subscription Plans.
    """
    __tablename__ = 'subscription_plans'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    price_monthly = db.Column(db.Float, nullable=False, default=0.0)
    currency = db.Column(db.String(3), default="EUR")

    # Features as JSON
    # Requires a database that supports JSON or storing as Text and parsing manually.
    # SQLite supports JSON in newer versions, but Text is safer for general compatibility if not using PostgreSQL specific types.
    # However, memory says "PostgreSQL and SQLAlchemy". So we can try JSON.
    # But usually db.JSON is generic enough in SQLAlchemy 1.4+.
    features_json = db.Column(db.JSON, nullable=True)

    is_active = db.Column(db.Boolean, default=True)