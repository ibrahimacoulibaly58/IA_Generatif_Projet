from prompts import *
from llm import call_llm, call_llm_with_retry, call_llm_stream

# ============================================================
# 🧠 AGENT PROFIL - Déduction des centres d'intérêt
# ============================================================
def profile_agent(destination, interests, stream=False):
    prompt = profile_prompt(destination, interests)

    if stream:
        return call_llm_stream(prompt, agent_type="profile")
    else:
        return call_llm_with_retry(prompt, agent_type="profile")


# ============================================================
# 🗺️ AGENT PLANIFICATEUR - Génération d'itinéraires
# ============================================================
def planner_agent(destination, start_date, end_date, interests, option_number=1, stream=False):
    prompt = planner_prompt(destination, start_date, end_date, interests, option_number)

    if stream:
        return call_llm_stream(prompt, agent_type="planner")
    else:
        return call_llm_with_retry(prompt, agent_type="planner")


def compare_itineraries(destination, option_a, option_b):
    prompt = planner_compare_prompt(destination, option_a, option_b)
    return call_llm_with_retry(prompt, agent_type="planner")


# ============================================================
# 🚄 AGENT TRANSPORT - Suggestions de transport
# ============================================================
def transport_agent(destination, start_date, end_date, origin="France", stream=False):
    prompt = transport_prompt(destination, start_date, end_date, origin)

    if stream:
        return call_llm_stream(prompt, agent_type="transport")
    else:
        return call_llm_with_retry(prompt, agent_type="transport")


# ============================================================
# 🏨 AGENT HÉBERGEMENT - Suggestions d'hôtels
# ============================================================
def hotel_agent(destination, start_date, end_date, budget="moyen", stream=False):
    prompt = hotel_prompt(destination, start_date, end_date, budget)

    if stream:
        return call_llm_stream(prompt, agent_type="hotel")
    else:
        return call_llm_with_retry(prompt, agent_type="hotel")


# ============================================================
# 📝 AGENT EXPORT - Formatage PDF et Email
# ============================================================
def export_agent(destination, itinerary, transport, hotel, user_name, user_email):
    prompt = export_pdf_prompt(destination, itinerary, transport, hotel, user_name, user_email)
    return call_llm_with_retry(prompt, agent_type="export")


def email_agent(destination, itinerary_summary, user_name):
    prompt = email_confirmation_prompt(destination, itinerary_summary, user_name)
    return call_llm_with_retry(prompt, agent_type="export")


# ============================================================
# 🧠 ORCHESTRATOR - Workflow complet
# ============================================================
def run_full_workflow(
    destination,
    start_date,
    end_date,
    interests="",
    origin="France",
    budget="moyen",
    user_name="",
    user_email=""
):
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

    # ÉTAPE 1 : Profil
    result["profile"] = profile_agent(destination, interests)

    if not interests or not interests.strip():
        interests = result["profile"]

    # ÉTAPE 2 : Itinéraires
    result["itinerary_option_a"] = planner_agent(
        destination, start_date, end_date, interests, option_number=1
    )

    result["itinerary_option_b"] = planner_agent(
        destination, start_date, end_date, interests, option_number=2
    )

    # ÉTAPE 3 : Comparaison
    result["comparison"] = compare_itineraries(
        destination,
        result["itinerary_option_a"],
        result["itinerary_option_b"]
    )

    # ÉTAPE 4 : Transport
    result["transport"] = transport_agent(
        destination, start_date, end_date, origin
    )

    # ÉTAPE 5 : Hôtel
    result["hotel"] = hotel_agent(
        destination, start_date, end_date, budget
    )

    # ÉTAPE 6 : Export
    result["export_content"] = export_agent(
        destination,
        result["itinerary_option_a"],
        result["transport"],
        result["hotel"],
        user_name,
        user_email
    )

    # ÉTAPE 7 : Email
    result["email_content"] = email_agent(
        destination,
        result["itinerary_option_a"][:500] if result["itinerary_option_a"] else "",
        user_name
    )

    return result


# ============================================================
# 🔄 STREAMING - Générateurs pour Streamlit
# ============================================================
def stream_profile(destination, interests):
    for chunk in profile_agent(destination, interests, stream=True):
        yield chunk


def stream_itinerary(destination, start_date, end_date, interests, option_number):
    for chunk in planner_agent(destination, start_date, end_date, interests, option_number, stream=True):
        yield chunk


def stream_transport(destination, start_date, end_date, origin):
    for chunk in transport_agent(destination, start_date, end_date, origin, stream=True):
        yield chunk


def stream_hotel(destination, start_date, end_date, budget):
    for chunk in hotel_agent(destination, start_date, end_date, budget, stream=True):
        yield chunk