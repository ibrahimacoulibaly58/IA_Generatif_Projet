def cot_prompt(destination, days):
    return f"""
Tu es un expert en voyage.

Analyse étape par étape :
1. Comprends la destination ({destination})
2. Prends en compte la durée ({days} jours)
3. Définis une stratégie optimale

Réponse claire et structurée.
"""

def tot_prompt(destination):
    return f"""
Propose 3 types de voyage pour {destination} :
- aventure
- détente
- culturel

Pour chaque :
- description
- type de voyageur
"""