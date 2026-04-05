import os
from groq import Groq
from dotenv import load_dotenv
import streamlit as st

# Charger les variables d'environnement
load_dotenv()

# Récupérer la clé API
api_key = os.getenv("GROQ_API_KEY")

# Vérification
if not api_key:
    raise ValueError("❌ Clé API GROQ introuvable. Vérifie ton fichier .env")

client = Groq(api_key=api_key)

# 🎯 System prompts par agent
SYSTEM_PROMPTS = {
    "default": "Tu es un assistant de voyage expert, utile et précis.",
    "planner": "Tu es un planificateur de voyage expert. Tu crées des itinéraires détaillés, réalistes et optimisés.",
    "transport": "Tu es un expert en transport (avion, train, bus). Tu proposes les meilleures options avec des liens de recherche.",
    "hotel": "Tu es un expert en hébergement. Tu suggères des quartiers et types d'hôtels adaptés au voyageur.",
    "profile": "Tu es un expert en profil voyageur. Tu déduis les centres d'intérêt selon la destination.",
    "export": "Tu es un expert en rédaction de documents. Tu formates les informations de manière claire et professionnelle."
}

# ============================================================
# ✅ VERSION NON-STREAM (corrigée)
# ============================================================
def call_llm(prompt, agent_type="default"):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS.get(agent_type, SYSTEM_PROMPTS["default"])},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Erreur LLM : {str(e)}"


# ============================================================
# ✅ VERSION STREAM (nouvelle)
# ============================================================
def call_llm_stream(prompt, agent_type="default"):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPTS.get(agent_type, SYSTEM_PROMPTS["default"])},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            stream=True
        )

        for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        yield f"❌ Erreur LLM : {str(e)}"


# ============================================================
# 🔁 RETRY (corrigé)
# ============================================================
def call_llm_with_retry(prompt, agent_type="default", max_retries=3):
    for i in range(max_retries):
        result = call_llm(prompt, agent_type)

        if result and not result.startswith("❌"):
            return result

    return f"❌ Erreur après {max_retries} tentatives"