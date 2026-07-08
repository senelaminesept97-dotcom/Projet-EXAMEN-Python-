# Gestion d'une Flotte de Véhicules en Location

Ce projet est une application de gestion de flotte hétérogène (voitures, utilitaires, motos) qui intègre les concepts avancés de la Programmation Orientée Objet (POO), le respect des règles métiers complexes (tarifications, entretiens, pénalités) et une stratégie de persistance multi-support (SQLite, JSON, CSV).

## Fonctionnalités Implémentées

1. **Gestion de Flotte Mixte (Fct 16)** : Initialisation d'une flotte d'au moins 8 véhicules répartis sur 3 types distincts.
2. **Cycle de Location Complet (Fct 17)** : Réservation, départ (mise à jour du statut) et calcul du tarif ajusté selon la durée et la catégorie du client.
3. **Alertes de Maintenance Automatiques (Fct 18)** : Détection des véhicules nécessitant un entretien selon des critères spécifiques (kilométrage ou ancienneté de la dernière révision).
4. **Rapport de Disponibilité (Fct 19)** : Requête sur une date cible pour lister les véhicules libres de toute location active.
5. **Calcul de Pénalité de Retard (Bonus - Fct 20)** : Majoration automatique du tarif journalier de 150 % pour chaque jour de retard lors du retour.

---

## Architecture du Projet

Le projet respecte l'arborescence standardisée suivante :

Gestion d'une Flotte de Véhicules en Location/
│
├── main.py              # Point d'entrée, scénarios de test et orchestrateur
├── config/
│   └── config.py        # Centralisation des chemins (BDD, exports JSON/CSV)
├── db/
│   ├── __init__.py
│   ├── connection.py    # Initialisation SQLite et gestion des connexions
│   └── operations.py    # Modèles objets (ABC), Agrégation, Composition et requêtes SQL
└── utils/
    ├── __init__.py
    └── helpers.py       # Énumérations (Statuts, Catégories) et classes de données

Concepts POO & Choix de Conception
•	Classe Abstraite (ABC) : VehiculeBase définit le contrat d'interface pour tous les types de véhicules. Les méthodes calculer_tarif_jour() et necessite_entretien() sont implémentées de manière polymorphique par les classes enfants (Voiture, Utilitaire, Moto).
•	Agrégation : La classe Flotte contient une liste de structures VehiculeBase. Les véhicules ont une durée de vie indépendante de la flotte et y sont rattachés dynamiquement.
•	Composition : Chaque véhicule crée et possède son propre historique d'Entretien. Si un véhicule est détruit ou supprimé, son historique d'entretien disparaît avec lui.
•	Énumérations : Utilisation stricte de StatutVehicule et CategorieClient pour sécuriser les états et interdire les valeurs aberrantes.
Stratégies de Persistance
Le système fait cohabiter trois modes de stockage :
1.	SQLite : Base relationnelle principale. Elle maintient les tables vehicules, locations (avec contrainte de clé étrangère) et entretiens. Elle sert à exécuter les requêtes de disponibilité à une date et le calcul du chiffre d'affaires par catégorie.
2.	JSON : Export/Import complet de l'état de la flotte. Gère la problématique du polymorphisme à la relecture grâce à un marqueur de type.
3.	CSV : Extraction à la demande des contrats de location actifs ou clôturés sur une période spécifique.
Installation et Lancement
Prérequis
•	Python 3.8 ou version supérieure.
•	Aucune dépendance externe requise (utilisation exclusive de la bibliothèque standard Python : sqlite3, json, csv, datetime, abc).
Exécution
Pour initialiser la base de données, charger la flotte de démonstration, exécuter le cycle de location (avec gestion des pénalités) et générer les rapports, lancez la commande suivante à la racine du dossier mon_projet/ :
Bash
python main.py
Fichiers générés après exécution :
•	db/flotte_vehicules.db : Base de données SQLite locale.
•	flotte_export.json : Sauvegarde complète de la flotte et des historiques d'entretien.
•	contrats_export.csv : Journal des contrats de location extraits sur la période.

