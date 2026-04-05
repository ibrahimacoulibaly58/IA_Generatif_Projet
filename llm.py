import os
from groq import Groq
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer la clé API
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("❌ Clé API GROQ introuvable. Vérifie ton fichier .env")

client = Groq(api_key=api_key)

# 🎯 System prompts par agent
SYSTEM_PROMPTS = {
    "default": "Tu es un assistant expert et précis. Pense étape par étape pour résoudre chaque problème.",
    "planner": "Tu es un planificateur expert. Décompose les problèmes étape par étape (CoT), explore plusieurs solutions (ToT) et choisis la meilleure.",
    "transport": "Tu es un expert en transport. Utilise ReAct : Pensée → Action → Observation → Réponse. Vérifie tes réponses (Self-Correction).",
    "hotel": "Tu es un expert en hébergement. Applique CoT et vérifie chaque suggestion.",
    "profile": "Tu es un expert en profil voyageur. Déduis les centres d'intérêt étape par étape et vérifie la cohérence.",
    "export": "Tu es un expert en rédaction de documents. Vérifie et corrige chaque contenu avant de le retourner."
}

# ============================================================
# ✅ VERSION NON-STREAM
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
# ✅ VERSION STREAM
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
# 🔁 RETRY
# ============================================================
def call_llm_with_retry(prompt, agent_type="default", max_retries=3):
    for i in range(max_retries):
        result = call_llm(prompt, agent_type)
        if result and not result.startswith("❌"):
            return result
    return f"❌ Erreur après {max_retries} tentatives"