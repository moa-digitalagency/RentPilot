
/*
* Nom de l'application : RentPilot
* Description : JavaScript logic for i18n.
* Produit de : MOA Digital Agency, www.myoneart.com
* Fait par : Aisance KALONJI, www.aisancekalonji.com
* Auditer par : La CyberConfiance, www.cyberconfiance.com
*/
window.translations = {};

async function loadTranslations() {
    // Try to get lang from html tag
    const lang = document.documentElement.lang || 'fr';

    try {
        const response = await fetch(`/api/lang/${lang}`);
        if (!response.ok) throw new Error('Failed to load translations');
        window.translations = await response.json();
        console.log('Translations loaded for:', lang);

        // Dispatch event so other scripts know translations are ready
        document.dispatchEvent(new Event('translationsLoaded'));
    } catch (error) {
        console.error('Error loading translations:', error);
    }
}

// Helper function to get text
window._t = function(key, params = {}) {
    const keys = key.split('.');
    let value = window.translations;

    for (const k of keys) {
        if (value && value[k]) {
            value = value[k];
        } else {
            return key; // Fallback to key
        }
    }

    // Simple interpolation {param}
    if (typeof value === 'string' && Object.keys(params).length > 0) {
        return value.replace(/{(\w+)}/g, (match, p1) => {
            return params[p1] !== undefined ? params[p1] : match;
        });
    }

    return value;
};

// Initialize
document.addEventListener('DOMContentLoaded', loadTranslations);