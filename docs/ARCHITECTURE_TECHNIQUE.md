# Architecture Technique

Ce document présente les choix techniques, l'organisation du code et les mécanismes de sécurité mis en œuvre dans la plateforme RentPilot.

## 1. Vue d'Ensemble

L'application est construite sur une architecture **Monolithique Modulaire** utilisant le framework **Flask** (Python). Elle suit le pattern **MVC** (Modèle-Vue-Contrôleur) où :
*   **Modèles** (`models/`) définissent la structure des données via SQLAlchemy.
*   **Vues** (`templates/`) génèrent le HTML côté serveur avec Jinja2 et TailwindCSS.
*   **Contrôleurs** (`routes/`) gèrent les requêtes HTTP et orchestrent la logique métier.

## 2. Stack Technologique

| Composant | Technologie | Description |
| :--- | :--- | :--- |
| **Backend** | Python 3.8+, Flask | Framework web léger et extensible. |
| **ORM** | SQLAlchemy | Abstraction de la base de données (supporte PostgreSQL). |
| **Frontend** | Jinja2, TailwindCSS, Alpine.js | Templates rendus côté serveur avec interactivité légère via JS. |
| **Base de Données** | PostgreSQL | Stockage relationnel robuste. |
| **Authentification** | Flask-Login | Gestion des sessions utilisateurs standards. |
| **Génération PDF** | ReportLab | Création dynamique de factures et reçus. |
| **Tests E2E** | Playwright | Automatisation des tests d'interface utilisateur. |

## 3. Structure du Projet

L'organisation des fichiers reflète la séparation des préoccupations :

*   `config/` : Configuration globale et variables d'environnement.
*   `models/` : Définitions des tables de la base de données (Schéma).
*   `routes/` : Blueprints Flask définissant les endpoints API et les pages web.
*   `services/` : Logique métier complexe (ex: calculs de coûts, rotation des tâches).
*   `templates/` : Fichiers HTML Jinja2.
*   `statics/` : Assets statiques (CSS, JS, Images, Uploads).
*   `tests/` : Scripts de test et de génération de preuves visuelles.

## 4. Modèle de Données (Schéma)

Le schéma relationnel est centré sur l'entité `Establishment` (Bien Immobilier) et `User` (Utilisateur).

### Entités Principales

1.  **Utilisateurs (`models/users.py`)**
    *   Rôles : `Admin`, `Bailleur`, `Tenant_Responsable`, `Colocataire`.
    *   Relations : Possède des baux, effectue des transactions, envoie des messages.

2.  **Établissements (`models/establishment.py`)**
    *   Représente une propriété ou une colocation.
    *   Configuration : Mode financier (Égal/Inégal), facturation SaaS.
    *   Comprends des `Rooms` (Chambres) et des `EstablishmentOwner` (Propriétaires multiples).

3.  **Finance (`models/finance.py`)**
    *   `Invoice` : Facture à payer (Loyer, Charges).
    *   `Transaction` : Paiement effectué par un locataire.
    *   `SaaSInvoice` : Facture de la plateforme envers le propriétaire.

4.  **Gestion Quotidienne**
    *   `ChoreType` / `ChoreEvent` (`models/chores.py`) : Gestion des tâches ménagères rotatives.
    *   `Ticket` (`models/maintenance.py`) : Signalement d'incidents techniques.

## 5. Mécanismes de Sécurité

### Authentification Hybride
L'application utilise deux méthodes d'authentification distinctes :
*   **Utilisateurs Standards** : Via base de données et `flask_login`.
*   **Super Admin** : Via des variables d'environnement (`SUPER_ADMIN_ID`, `SUPER_ADMIN_PASS`), contournant la base de données pour un accès de secours garanti.

### Contrôle d'Accès (RBAC)
Des décorateurs Python sécurisent les routes sensibles :
*   `@login_required` : Accès authentifié générique.
*   `@landlord_required` : Vérifie que l'utilisateur est bien propriétaire de l'établissement ciblé.
*   `@super_admin_required` : Restreint l'accès aux routes d'administration globale.

### Protection des Données
*   **Sanitization** : Les routes publiques (ex: vérification de ticket) renvoient des DTOs filtrés pour éviter la fuite d'informations sensibles.
*   **CSRF** : Protection des formulaires via `Flask-WTF`.
*   **Isolation des Données** : Les locataires ne peuvent voir que les données relatives à leur propre établissement (ex: `ChoreType`).

## 6. Logique Métier (Services)

La logique complexe est encapsulée dans le dossier `services/` pour faciliter la maintenance et les tests :

*   `FinanceService` : Algorithmes de répartition des coûts entre locataires.
*   `ChoreService` : Attribution automatique des tâches et validation par consensus.
*   `PDFService` : Génération de documents officiels avec QR Codes de vérification.
*   `I18nService` : Gestion multilingue (FR, EN, ES, PT).
