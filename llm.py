import os
from groq import Groq
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Récupérer la clé API
api_key = os.getenv("GROQ_API_KEY")

# Vérification (optionnel mais utile)
if not api_key:
    raise ValueError("❌ Clé API introuvable. Vérifie ton fichier .env")

client = Groq(api_key=api_key)

def call_llm(prompt):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Tu es un expert en voyage."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Erreur LLM : {str(e)}"