
"""
* Nom de l'application : RentPilot
* Description : Source file: seo_manager.py
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
"""
from models.saas_config import PlatformSettings

class SEOManager:
    @staticmethod
    def get_meta_tags(page_title=None):
        """
        Returns a dictionary with 'title' and 'description' based on PlatformSettings.
        """
        try:
            settings = PlatformSettings.query.first()
            template = settings.seo_title_template if settings and settings.seo_title_template else "%s | RentPilot"
            desc = settings.seo_meta_desc if settings and settings.seo_meta_desc else "SaaS de gestion locative moderne."
        except Exception:
            template = "%s | RentPilot"
            desc = "SaaS de gestion locative moderne."

        if page_title:
            try:
                final_title = template % page_title
            except TypeError:
                # Fallback if template doesn't have %s or has multiple
                final_title = f"{page_title} | RentPilot"
        else:
            # Clean up template if no page title
            final_title = template.replace("%s | ", "").replace(" | %s", "").replace("%s", "Accueil")

        return {
            'title': final_title,
            'description': desc
        }

    @staticmethod
    def generate_sitemap(base_url):
        """
        Generates a simple XML sitemap string.
        """
        # Ensure base_url doesn't have trailing slash
        if base_url.endswith('/'):
            base_url = base_url[:-1]

        urls = ['/', '/login', '/register']

        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        for u in urls:
            xml += f'  <url>\n    <loc>{base_url}{u}</loc>\n    <changefreq>monthly</changefreq>\n  </url>\n'
        xml += '</urlset>'
        return xml

    @staticmethod
    def generate_robots_txt(base_url):
        """
        Generates content for robots.txt.
        """
        if base_url.endswith('/'):
            base_url = base_url[:-1]

        return f"User-agent: *\nDisallow: /dashboard/\nDisallow: /admin/\nSitemap: {base_url}/sitemap.xml"