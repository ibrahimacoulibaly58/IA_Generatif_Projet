# 🌍 Planificateur de Voyage Autonome  
### Projet IA Générative — Agents LLM & Raisonnement Avancé

Ce projet propose un assistant de voyage intelligent capable de planifier un séjour complet grâce à des techniques modernes de raisonnement appliquées aux modèles de langage (LLM).  
L’application fonctionne via une interface **Streamlit** et s’appuie sur plusieurs stratégies avancées : **ReAct**, **Chain of Thought**, **Tree of Thoughts**, et **Self‑Correction**.

---

## ✨ Fonctionnalités

### 🧠 Raisonnement avancé
L’agent utilise plusieurs techniques complémentaires :

- **ReAct (Reason + Act)**  
  Le modèle réfléchit, choisit une action, appelle un outil (météo, vols), observe le résultat, puis continue son raisonnement.

- **Chain of Thought (CoT)**  
  Le modèle décompose explicitement son raisonnement étape par étape.

- **Tree of Thoughts (ToT)**  
  Génération de plusieurs itinéraires candidats → évaluation → sélection du meilleur.

- **Self‑Correction**  
  L’agent critique son propre itinéraire et génère une version corrigée.

---

## 🧳 Capacités de l’assistant

- Analyse de la demande utilisateur  
- Récupération de la météo réelle via API  
- Recherche de vols simulés  
- Génération d’activités adaptées au climat  
- Création d’un itinéraire jour par jour  
- Téléchargement du planning final  
- Affichage des traces de raisonnement (ReAct)

---

## 📁 Structure du projet

📦 Projet  
┣ 📜 app.py — Interface Streamlit  
┣ 📜 orchestrator.py — Orchestration ReAct / ToT / Self-Correction  
┣ 📜 reasoning.py — Implémentation des techniques de raisonnement  
┣ 📜 tools.py — Outils externes (météo, vols)  
┣ 📜 llm.py — Appels LLM unifiés  
┣ 📜 config.py — Configuration des modèles et endpoints  
┗ 📜 README.md  

---

## 🔧 Installation

### 1. Cloner le projet



# Installer les dépendances
pip install -r requirements.txt

# Lancer l’application
streamlit run app.py

---

## GitHub

[https://github.com/ibrahimacoulibaly58/IA_Generatif_Projet](https://github.com/ibrahimacoulibaly58/IA_Generatif_Projet)
