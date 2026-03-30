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

# 🎯 System prompts par agent (pour personnaliser le comportement)
SYSTEM_PROMPTS = {
    "default": "Tu es un assistant de voyage expert, utile et précis.",
    "planner": "Tu es un planificateur de voyage expert. Tu crées des itinéraires détaillés, réalistes et optimisés.",
    "transport": "Tu es un expert en transport (avion, train, bus). Tu proposes les meilleures options avec des liens de recherche.",
    "hotel": "Tu es un expert en hébergement. Tu suggères des quartiers et types d'hôtels adaptés au voyageur.",
    "profile": "Tu es un expert en profil voyageur. Tu déduis les centres d'intérêt selon la destination.",
    "export": "Tu es un expert en rédaction de documents. Tu formates les informations de manière claire et professionnelle."
}

def call_llm(prompt, agent_type="default", stream=False):
    """
    Appel au LLM Groq avec support optionnel du streaming.
    
    Args:
        prompt: Le prompt utilisateur
        agent_type: Type d'agent pour le system prompt (planner, transport, hotel, etc.)
        stream: Si True, retourne un générateur pour le streaming
    
    Returns:
        str ou generator: La réponse complète ou un générateur de tokens
    """
    try:
        if stream:
            # Mode streaming pour affichage en temps réel
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPTS.get(agent_type, SYSTEM_PROMPTS["default"])},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                stream=True
            )
            # Générateur qui yield chaque chunk
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        else:
            # Mode classique (réponse complète)
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
        if stream:
            yield f"❌ Erreur LLM : {str(e)}"
        else:
            return f"❌ Erreur LLM : {str(e)}"


def call_llm_with_retry(prompt, agent_type="default", max_retries=3):
    """
    Appel avec mécanisme de retry en cas d'échec.
    """
    for i in range(max_retries):
        try:
            result = call_llm(prompt, agent_type, stream=False)
            if not result.startswith("❌ Erreur"):
                return result
        except Exception as e:
            if i == max_retries - 1:
                return f"❌ Erreur après {max_retries} tentatives : {str(e)}"
    return None