import streamlit as st
import openai
from config import MODELS, BASE_URLS

def call_llm(messages, temperature=0.7, provider="groq"):
    """Appel LLM unifié avec gestion d'erreurs"""
    if not st.session_state.get("api_key"):
        st.warning("⚠️ Clé API manquante dans la sidebar.")
        return None
    try:
        client = openai.OpenAI(api_key=st.session_state.api_key, base_url=BASE_URLS[provider])
        resp = client.chat.completions.create(
            model=MODELS[provider], messages=messages, 
            temperature=temperature, response_format={"type": "text"}
        )
        return resp.choices[0].message.content.strip()
    except openai.RateLimitError:
        st.error("⚠️ Quota dépassé. Patientez ou vérifiez votre plan.")
        return None
    except openai.AuthenticationError:
        st.error("🔑 Clé invalide.")
        return None
    except Exception as e:
        st.error(f"❌ Erreur LLM: {str(e)[:120]}")
        return None