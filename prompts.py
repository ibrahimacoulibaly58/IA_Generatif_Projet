# ============================================================
# 🧠 AGENT PROFIL - Déduction des centres d'intérêt
# ============================================================
def profile_prompt(destination, interests):
    if interests and interests.strip():
        return f"""
L'utilisateur a des centres d'intérêt : {interests}
Destination : {destination}

Confirme et enrichis ces centres d'intérêt avec des suggestions pertinentes pour cette destination.
Réponds sous forme de liste à puces.
"""
    else:
        return f"""
L'utilisateur n'a pas spécifié de centres d'intérêt pour {destination}.

Analyse cette destination et suggère automatiquement 3-5 centres d'intérêt pertinents
(ex: culture, gastronomie, aventure, détente, histoire, nature, etc.)

Réponds sous forme de liste à puces concise.
"""

# ============================================================
# 🗺️ AGENT PLANIFICATEUR - Génération d'itinéraires
# ============================================================
def planner_prompt(destination, start_date, end_date, interests, option_number):
    return f"""
Crée un itinéraire de voyage pour {destination}.

📅 Dates : Du {start_date} au {end_date}
🎯 Centres d'intérêt : {interests if interests else "À toi de suggérer les plus pertinents"}

⚠️ C'est l'OPTION {option_number} sur 2 proposées.
Propose une approche légèrement différente de l'autre option (ex: plus culturel vs plus détente).

Format attendu :
## Jour 1 - [Titre de la journée]
**Matin :** [Activité]
**Après-midi :** [Activité]
**Soir :** [Activité]

## Jour 2 - [Titre de la journée]
...

Sois précis, réaliste et tiens compte des temps de trajet.
"""

def planner_compare_prompt(destination, option_a, option_b):
    return f"""
Voici 2 options d'itinéraire pour {destination}:

OPTION A:
{option_a}

OPTION B:
{option_b}

Fais un résumé comparatif court (3-4 lignes) pour aider l'utilisateur à choisir.
Mets en avant les différences principales (rythme, activités, style).
"""

# ============================================================
# 🚄 AGENT TRANSPORT - Suggestions de transport
# ============================================================
def transport_prompt(destination, start_date, end_date, origin="France"):
    return f"""
Propose des options de transport pour un voyage à {destination}.

📅 Dates : Du {start_date} au {end_date}
🛫 Lieu de départ : {origin}

Pour chaque mode de transport (Avion, Train, Bus, Voiture), donne :
1. Compagnies recommandées
2. Durée estimée du trajet
3. Fourchette de prix estimée
4. **Lien de recherche pré-rempli** (ex: Google Flights, SNCF, etc.)

Format :
### ✈️ Avion
- Compagnies : ...
- Durée : ...
- Prix : ...
- 🔗 [Lien de recherche](...)

### 🚆 Train
...

Sois réaliste sur les options disponibles.
"""

# ============================================================
# 🏨 AGENT HÉBERGEMENT - Suggestions d'hôtels
# ============================================================
def hotel_prompt(destination, start_date, end_date, budget="moyen"):
    return f"""
Propose des options d'hébergement pour {destination}.

📅 Dates : Du {start_date} au {end_date}
💰 Budget : {budget}

Pour chaque option, donne :
1. Quartier recommandé (avec avantages)
2. Type d'hébergement (hôtel, Airbnb, auberge, etc.)
3. Fourchette de prix par nuit
4. **Lien de recherche pré-rempli** (ex: Booking, Airbnb)

Format :
### 🏨 Option 1 - [Nom du quartier]
- Type : ...
- Prix/nuit : ...
- Avantages : ...
- 🔗 [Lien de recherche](...)

Propose 3 options différentes.
"""

# ============================================================
# 📝 AGENT EXPORT - Formatage PDF et Email
# ============================================================
def export_pdf_prompt(destination, itinerary, transport, hotel, user_name, user_email):
    return f"""
Génère un résumé de voyage complet et bien formaté pour impression PDF.

Destination : {destination}
Voyageur : {user_name}
Email : {user_email}

ITINÉRAIRE :
{itinerary}

TRANSPORT :
{transport}

HÉBERGEMENT :
{hotel}

Formatage requis :
- Utilise des titres clairs (##, ###)
- Liste à puces pour les activités
- Inclure une section "Informations pratiques" (décalage horaire, devise, langue, etc.)
- Ton professionnel et enthousiaste

Ce texte sera converti en PDF, donc sois structuré.
"""

def email_confirmation_prompt(destination, itinerary_summary, user_name):
    return f"""
Rédige un email de confirmation de voyage à envoyer à {user_name}.

Destination : {destination}
Résumé : {itinerary_summary}

L'email doit :
- Être chaleureux et professionnel
- Résumer les points clés du voyage
- Inclure une invitation à contacter pour modifications
- Avoir un objet d'email clair

Format :
Objet : [Objet de l'email]

Corps de l'email :
[Contenu]
"""

# ============================================================
# 🧠 CHAIN OF THOUGHT - Analyse initiale
# ============================================================
def cot_prompt(destination, start_date, end_date, interests):
    return f"""
Tu es un expert en voyage. Analyse cette demande étape par étape :

🌍 Destination : {destination}
📅 Dates : Du {start_date} au {end_date}
🎯 Intérêts : {interests if interests else "Non spécifiés - à déduire"}

Étapes d'analyse :
1. Vérifier la faisabilité (saison, durée, accès)
2. Identifier les contraintes potentielles (météo, événements, etc.)
3. Définir une stratégie optimale pour ce voyage

Réponse structurée et concise.
"""

# ============================================================
# 🌳 TREE OF THOUGHTS - Alternatives de voyage
# ============================================================
def tot_prompt(destination, style):
    return f"""
Propose un concept de voyage pour {destination} avec le style : {style}.

Styles possibles : aventure, détente, culturel, gastronomique, familial, romantique

Pour ce style, donne :
- Description du concept (2-3 phrases)
- Type de voyageur ciblé
- 3 activités phares
- Budget estimé (€)

Sois créatif et réaliste.
"""