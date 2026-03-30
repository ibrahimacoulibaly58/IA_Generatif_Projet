from prompts import *
from llm import call_llm, call_llm_with_retry

# ============================================================
# 🧠 AGENT PROFIL - Déduction des centres d'intérêt
# ============================================================
def profile_agent(destination, interests, stream=False):
    """
    Analyse la destination et déduit/suggère les centres d'intérêt.
    """
    prompt = profile_prompt(destination, interests)
    
    if stream:
        return call_llm(prompt, agent_type="profile", stream=True)
    else:
        return call_llm_with_retry(prompt, agent_type="profile")


# ============================================================
# 🗺️ AGENT PLANIFICATEUR - Génération d'itinéraires
# ============================================================
def planner_agent(destination, start_date, end_date, interests, option_number=1, stream=False):
    """
    Génère un itinéraire détaillé pour une option donnée (1 ou 2).
    """
    prompt = planner_prompt(destination, start_date, end_date, interests, option_number)
    
    if stream:
        return call_llm(prompt, agent_type="planner", stream=True)
    else:
        return call_llm_with_retry(prompt, agent_type="planner")


def compare_itineraries(destination, option_a, option_b):
    """
    Compare 2 options d'itinéraire pour aider au choix.
    """
    prompt = planner_compare_prompt(destination, option_a, option_b)
    return call_llm_with_retry(prompt, agent_type="planner")


# ============================================================
# 🚄 AGENT TRANSPORT - Suggestions de transport
# ============================================================
def transport_agent(destination, start_date, end_date, origin="France", stream=False):
    """
    Propose des options de transport avec liens de recherche.
    """
    prompt = transport_prompt(destination, start_date, end_date, origin)
    
    if stream:
        return call_llm(prompt, agent_type="transport", stream=True)
    else:
        return call_llm_with_retry(prompt, agent_type="transport")


# ============================================================
# 🏨 AGENT HÉBERGEMENT - Suggestions d'hôtels
# ============================================================
def hotel_agent(destination, start_date, end_date, budget="moyen", stream=False):
    """
    Propose des options d'hébergement avec liens de recherche.
    """
    prompt = hotel_prompt(destination, start_date, end_date, budget)
    
    if stream:
        return call_llm(prompt, agent_type="hotel", stream=True)
    else:
        return call_llm_with_retry(prompt, agent_type="hotel")


# ============================================================
# 📝 AGENT EXPORT - Formatage pour PDF et Email
# ============================================================
def export_agent(destination, itinerary, transport, hotel, user_name, user_email):
    """
    Formate toutes les informations pour l'export PDF.
    """
    prompt = export_pdf_prompt(destination, itinerary, transport, hotel, user_name, user_email)
    return call_llm_with_retry(prompt, agent_type="export")


def email_agent(destination, itinerary_summary, user_name):
    """
    Génère le contenu de l'email de confirmation.
    """
    prompt = email_confirmation_prompt(destination, itinerary_summary, user_name)
    return call_llm_with_retry(prompt, agent_type="export")


# ============================================================
# 🧠 ORCHESTRATOR - Gestion du workflow complet
# ============================================================
def run_full_workflow(
    destination,
    start_date,
    end_date,
    interests="",
    origin="France",
    budget="moyen",
    user_name="",
    user_email="",
    stream=False
):
    """
    Orchestre l'ensemble du workflow de voyage étape par étape.
    
    Returns:
        dict: Toutes les informations du voyage structurées
    """
    result = {
        "profile": None,
        "itinerary_option_a": None,
        "itinerary_option_b": None,
        "comparison": None,
        "selected_itinerary": None,
        "transport": None,
        "hotel": None,
        "export_content": None,
        "email_content": None
    }
    
    # ÉTAPE 1: Analyse du profil et centres d'intérêt
    result["profile"] = profile_agent(destination, interests, stream=False)
    
    # Si aucun intérêt spécifié, on utilise ceux suggérés par l'agent
    if not interests or not interests.strip():
        interests = result["profile"]
    
    # ÉTAPE 2: Génération de 2 options d'itinéraire
    result["itinerary_option_a"] = planner_agent(
        destination, start_date, end_date, interests, option_number=1, stream=False
    )
    
    result["itinerary_option_b"] = planner_agent(
        destination, start_date, end_date, interests, option_number=2, stream=False
    )
    
    # ÉTAPE 3: Comparaison des options
    result["comparison"] = compare_itineraries(
        destination, 
        result["itinerary_option_a"], 
        result["itinerary_option_b"]
    )
    
    # ÉTAPE 4: Transport (après validation de l'itinéraire - simulé)
    result["transport"] = transport_agent(
        destination, start_date, end_date, origin, stream=False
    )
    
    # ÉTAPE 5: Hébergement (après validation de l'itinéraire - simulé)
    result["hotel"] = hotel_agent(
        destination, start_date, end_date, budget, stream=False
    )
    
    # ÉTAPE 6: Export PDF
    result["export_content"] = export_agent(
        destination,
        result["itinerary_option_a"],  # Par défaut option A
        result["transport"],
        result["hotel"],
        user_name,
        user_email
    )
    
    # ÉTAPE 7: Email de confirmation
    result["email_content"] = email_agent(
        destination,
        result["itinerary_option_a"][:500],  # Résumé court
        user_name
    )
    
    return result


# ============================================================
# 🔄 FONCTIONS POUR LE STREAMING ÉTAPE PAR ÉTAPE
# ============================================================
def stream_profile(destination, interests):
    """Générateur pour streaming du profil"""
    for chunk in profile_agent(destination, interests, stream=True):
        yield chunk


def stream_itinerary(destination, start_date, end_date, interests, option_number):
    """Générateur pour streaming de l'itinéraire"""
    for chunk in planner_agent(destination, start_date, end_date, interests, option_number, stream=True):
        yield chunk


def stream_transport(destination, start_date, end_date, origin):
    """Générateur pour streaming du transport"""
    for chunk in transport_agent(destination, start_date, end_date, origin, stream=True):
        yield chunk


def stream_hotel(destination, start_date, end_date, budget):
    """Générateur pour streaming de l'hôtel"""
    for chunk in hotel_agent(destination, start_date, end_date, budget, stream=True):
        yield chunk