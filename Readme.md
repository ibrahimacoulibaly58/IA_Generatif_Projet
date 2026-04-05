# Travel Planner AI – Planificateur de Voyage Intelligent

Un projet d’IA pour créer des voyages sur mesure en utilisant plusieurs agents spécialisés et le modèle LLaMA 3.1 via Groq.

---

## Description

Travel Planner AI permet à un utilisateur de générer un voyage personnalisé étape par étape. Le projet intègre plusieurs agents pour gérer :

* Les centres d’intérêt du voyageur
* La génération d’itinéraires
* Les options de transport
* Les suggestions d’hébergement
* La création de documents PDF et d’e-mails de confirmation

Le tout avec un **workflow interactif** et **streaming temps réel**.

---

## Fonctionnalités

* Étape par étape : du choix de la destination à la confirmation finale
* Génération de deux options d’itinéraire et comparaison automatique
* Recherche de transport avec estimation du prix et durée
* Suggestions d’hébergement selon le budget
* Export PDF du voyage et génération d’e-mails
* Streaming en temps réel des réponses des agents
* Sauvegarde et réinitialisation du voyage

---

## Technologies

* Python 3.11+
* [Streamlit](https://streamlit.io/) pour l’interface web
* [Groq LLaMA 3.1](https://www.groq.com/) pour le modèle LLM
* dotenv pour gérer les clés API
* Fichiers `.env` pour les configurations

---

## Installation

Installer les dépendances Python :

```bash
pip install -r requirements.txt
```

---

## Utilisation

Lancer l'application Streamlit :

```bash
streamlit run app.py
```

---

## Architecture du projet

TravelPlannerAI/
│
├─ app.py              # Interface principale Streamlit
├─ agent.py            # Agents et orchestration (profil, itinéraire, transport, hôtel, export)
├─ prompts.py          # Prompts LLM pour chaque agent
├─ llm.py              # Communication avec LLM Groq et gestion du streaming
├─ utils.py            # Fonctions utilitaires (session, PDF, email, navigation)
├─ requirements.txt    # Dépendances Python
├─ .env                # Clés API et configuration
└─ README.md           # Documentation du projet

---

## Agents utilisés

* Profil agent
* Planificateur agent
* Transport agent
* Hôtel agent
* Export agent (PDF & Email)

---

## Streaming

Toutes les réponses des agents peuvent être affichées en temps réel via le streaming pour une meilleure expérience utilisateur.

---

## Contribution

Contributions ouvertes via pull requests sur le dépôt GitHub.

---

## Licence

MIT License

---

## GitHub

[https://github.com/ibrahimacoulibaly58/IA_Generatif_Projet](https://github.com/ibrahimacoulibaly58/IA_Generatif_Projet)
