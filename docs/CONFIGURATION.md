# Configuration et Déploiement

Ce document détaille l'ensemble des variables d'environnement nécessaires au bon fonctionnement de l'application RentPilot, ainsi que les instructions d'installation et de déploiement.

## 1. Prérequis Système

*   **Python**: Version 3.8 ou supérieure.
*   **Base de Données**: PostgreSQL (Requis).
*   **Serveur Web**: Un serveur compatible WSGI (ex: Gunicorn) derrière un reverse proxy (ex: Nginx).

## 2. Installation des Dépendances

Clonez le dépôt et installez les paquets Python requis :

```bash
git clone <url_du_repo>
cd rentpilot
pip install -r requirements.txt
```

## 3. Variables d'Environnement

Le fichier `config/settings.py` centralise la configuration de l'application. Vous pouvez définir ces valeurs via un fichier `.env` à la racine du projet ou directement dans l'environnement du système d'exploitation.

| Variable | Description | Valeur par Défaut (Dev) | Obligatoire (Prod) |
| :--- | :--- | :--- | :--- |
| `FLASK_ENV` | Environnement d'exécution (`development` ou `production`). | `development` | Oui |
| `SECRET_KEY` | Clé secrète pour signer les sessions et sécuriser les formulaires CSRF. | `dev_secret_key...` | **Oui** (Critique) |
| `DB_URI` | Chaîne de connexion à la base de données (SQLAlchemy). | `postgresql://rentpilot:rentpilot@localhost:5432/rentpilot` | Oui |
| `UPLOAD_FOLDER` | Chemin absolu ou relatif pour le stockage des fichiers généraux (preuves, factures). | `statics/uploads` | Non |
| `UPLOAD_FOLDER_CHAT` | Chemin pour le stockage des médias du chat. | `statics/uploads/chat` | Non |
| `SUPER_ADMIN_ID` | Email de l'administrateur principal (Super Admin). | `admin@rentpilot.com` | Recommandé |
| `SUPER_ADMIN_PASS` | Mot de passe de l'administrateur principal. | `SuperSecretPass123!` | **Oui** (Critique) |

### Exemple de fichier `.env` pour la Production

```bash
FLASK_ENV=production
SECRET_KEY=une_chaine_aleatoire_tres_longue_et_securisee
DB_URI=postgresql://user:password@localhost:5432/rentpilot_db
SUPER_ADMIN_ID=admin@mondomaine.com
SUPER_ADMIN_PASS=MonMotDePasseComplexe!
```

## 4. Initialisation de la Base de Données

Avant de lancer l'application, vous devez initialiser la structure de la base de données. Utilisez le script fourni :

```bash
python init_db.py
```

Ce script va :
1.  Créer les tables si elles n'existent pas.
2.  Appliquer les migrations automatiques (ajout de colonnes manquantes).
3.  Vérifier l'intégrité des modèles.

## 5. Lancement de l'Application

### En Développement

Pour lancer le serveur de développement Flask :

```bash
python main.py
```
L'application sera accessible sur `http://localhost:5000`.

### En Production (Gunicorn)

Il est recommandé d'utiliser Gunicorn avec plusieurs workers :

```bash
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```

## 6. Maintenance et Scripts Utiles

*   **Vérification d'Audit** : `scripts/audit_check.py` effectue une analyse statique pour vérifier l'intégrité des modèles et des routes.
*   **Génération de Preuves Visuelles** : `tests/generate_visual_proofs.py` lance des scénarios utilisateurs simulés via Playwright pour valider le frontend.
