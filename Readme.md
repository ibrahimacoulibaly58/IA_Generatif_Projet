#  Planificateur de Voyage Intelligent avec Agents IA

##  Objectif
Ce projet consiste à développer une application Streamlit utilisant des agents intelligents basés sur des LLM pour planifier automatiquement un voyage.

---

##  Architecture

L'application repose sur une architecture multi-agents :

-  Agent 1 (Planificateur) :
  Génère la météo, les activités et un itinéraire initial.

-  Agent 2 (Critique) :
  Analyse l’itinéraire, détecte les incohérences et propose une version améliorée.

---

##  Techniques de raisonnement utilisées

### ✅ Chain of Thought (CoT)
Le modèle analyse la demande étape par étape pour structurer sa réflexion.

### ✅ ReAct (Reason + Act)
L’agent suit une boucle :
Analyse → Action → Observation → Amélioration

### ✅ Tree of Thoughts (ToT)
Plusieurs stratégies de voyage sont explorées (aventure, détente, culturel).

### ✅ Multi-Agents
Deux agents collaborent :
- un pour générer
- un pour critiquer et améliorer

---

##  Fonctionnalités

- Génération automatique d’un voyage
- Météo simulée
- Activités adaptées
- Itinéraire jour par jour
- Analyse critique
- Téléchargement du plan

---

##  Lancement

```bash
pip install -r requirements.txt
streamlit run app.py