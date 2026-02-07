# RentPilot QA & Showcase Scripts

Ce dossier contient des scripts d'automatisation pour la QA et la démonstration (Showcase) de RentPilot.

## `tests/generate_proofs.py`

Ce script utilise **Playwright** pour simuler un parcours utilisateur complet (Super Admin, Bailleur, Colocataire, Public), vérifier la logique financière et générer des preuves visuelles (screenshots).

### Pré-requis

1.  **Python 3.8+**
2.  **Playwright** et les navigateurs :

```bash
pip install playwright
playwright install
```

3.  **Dépendances du projet** (Flask, SQLAlchemy, etc.) doivent être installées :

```bash
pip install -r requirements.txt
```

### Utilisation

1.  Assurez-vous que le port **5000** est libre.
2.  Lancez le script depuis la racine du projet :

```bash
python3 tests/generate_proofs.py
```

### Scénario exécuté

Le script va automatiquement :
1.  **Reset DB** : Réinitialiser la base de données avec des données de test (1000€ Loyer, 4 Chambres).
2.  **Admin** : Changer le branding (Violet) et vérifier le dashboard.
3.  **Bailleur** : Configurer la répartition des charges et valider un paiement.
4.  **Colocataire** : Vérifier que sa part est bien de **250 €** (1000/4), changer la langue, poster un message et créer un ticket.
5.  **Public** : Vérifier un reçu valide et un reçu invalide.

### Résultats

Les screenshots seront sauvegardés dans le dossier :
`tests/proofs/`

Les fichiers générés incluent :
*   `01_admin_branding.png`
*   `02_admin_dashboard.png`
*   `03_landlord_setup.png`
*   `04_landlord_validation.png`
*   `05_tenant_dashboard_fr.png`
*   `06_tenant_dashboard_en.png`
*   `07_chat_interface.png`
*   `08_ticket_creation.png`
*   `09_landing_es.png`
*   `10_public_verification_success.png`
*   `11_public_verification_fail.png`
