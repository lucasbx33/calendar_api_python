# Projet Calendrier API Python

**Développeurs :** REYNAUD Lucas et JARDY Anthony

## Description du Projet

Ce projet permet une interaction directe avec Google Calendar. Les utilisateurs peuvent se connecter à leur agenda Google et accéder à leurs événements programmés. L'application offre plusieurs fonctionnalités :

- **Affichage des Événements :** Chaque événement est présenté avec son titre, sa date, et ses horaires.
- **Modification et Suppression :** Les utilisateurs peuvent modifier ou supprimer des événements directement depuis l'interface.
- **Ajout d’Événements :** Un formulaire en bas de page permet d'ajouter de nouveaux événements qui seront synchronisés avec l'agenda Google.

## Instructions d'Installation

Avant de commencer à utiliser l'application, veuillez suivre ces étapes :

1. **Installation des Dépendances :** Exécutez `pip install -r requirements.txt` pour installer toutes les dépendances nécessaires.
2. **Configuration du Serveur :** Le serveur local doit impérativement être lancé à l'adresse `http://127.0.0.1:5000/`. Cette adresse IP et port spécifiques sont requis car la connexion à Google pour ce projet n'est autorisée que pour cette IP.

## Démarrage de l'Application

Pour démarrer l'application, lancez le serveur sur `http://127.0.0.1:5000/` et connectez-vous avec vos identifiants Google pour accéder à votre agenda.
