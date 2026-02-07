# Fonctionnalités et Règles Métier

Ce document décrit les fonctionnalités clés de la plateforme RentPilot, en mettant l'accent sur la valeur ajoutée pour les propriétaires et les locataires, ainsi que sur les règles de gestion spécifiques.

## 1. Vue d'Ensemble

RentPilot est une solution SaaS (Software as a Service) conçue pour simplifier la gestion locative, particulièrement adaptée aux colocations et aux immeubles de rapport. Elle centralise la communication, les finances et la vie quotidienne des occupants.

## 2. Gestion des Rôles

La plateforme distingue plusieurs types d'utilisateurs avec des permissions spécifiques :

*   **Bailleur (Propriétaire)** : Gère les baux, suit les paiements, reçoit les tickets de maintenance.
*   **Locataire (Colocataire)** : Paye son loyer, déclare des incidents, valide les tâches ménagères.
*   **Administrateur** : Supervise l'ensemble de la plateforme (revenus SaaS, statistiques globales).

## 3. Module Financier

Le cœur du système repose sur une gestion transparente des flux financiers.

### Facturation et Paiements
*   **Loyer et Charges** : Le système génère automatiquement les appels de loyer et les factures de charges (eau, électricité, internet).
*   **Répartition des Coûts** :
    *   **Mode Égal** : Les charges communes sont divisées équitablement entre les occupants présents.
    *   **Mode Inégal** : Permet une répartition pondérée (ex: selon la surface de la chambre).
*   **Preuve de Paiement** : Les locataires téléversent une preuve (virement, chèque) qui doit être validée par le bailleur.

### Facturation SaaS
La plateforme elle-même facture ses services (abonnement) soit au propriétaire, soit directement aux locataires (en surplus du loyer), selon la configuration de l'établissement.

## 4. Vie Quotidienne et Colocation

RentPilot intègre des outils pour pacifier la vie en communauté.

### Gestion des Tâches Ménagères (Chores)
*   **Rotation Automatique** : Le système attribue les tâches (ménage, poubelles) aux locataires selon un algorithme rotatif équitable.
*   **Validation par les Pairs** : Une tâche n'est considérée comme "Faite" que si elle est validée par un autre colocataire (système de consensus N-1).
*   **Preuve Visuelle** : Possibilité d'ajouter une photo pour prouver la réalisation.

### Communication
*   **Chat Intégré** : Messagerie instantanée par établissement pour les échanges rapides.
*   **Annonces Officielles** : Le bailleur peut diffuser des informations importantes à tous les locataires.

## 5. Maintenance et Incidents

### Système de Tickets
Les locataires peuvent signaler des problèmes techniques (ex: fuite d'eau, panne chauffage) via un formulaire dédié :
*   **Priorité** : Urgence du problème.
*   **Photo** : Preuve visuelle de l'incident.
*   **Suivi** : Le bailleur met à jour le statut (Ouvert, En Cours, Résolu) pour tenir les locataires informés.

## 6. Personnalisation (Marque Blanche)

La plateforme est conçue pour être déployée en marque blanche :
*   **Identité Visuelle** : Logo, couleurs primaires/secondaires configurables.
*   **Documents** : Les reçus et factures sont générés au format PDF (A4 ou Ticket Thermique) avec l'en-tête de l'établissement.
*   **SEO & Textes** : Titres, descriptions et pieds de page sont modifiables depuis l'administration.

## 7. Sécurité et Conformité

*   **Vérification QR Code** : Chaque reçu de paiement généré contient un QR Code unique permettant à un tiers de vérifier son authenticité en ligne sans connexion requise.
*   **Historique** : Traçabilité complète des actions (paiements, validations de tâches, messages).
