import streamlit as st
import openai
import requests
import json
import re
from datetime import datetime, timedelta
import os

# -----------------------------------------------------------------------------
# CONFIGURATION & UTILITAIRES
# -----------------------------------------------------------------------------
st.set_page_config(page_title="🌍 Planificateur de Voyage Autonome", layout="wide")

# Sidebar : Configuration API
st.sidebar.title("⚙️ Configuration")
provider = st.sidebar.selectbox("🔌 Fournisseur LLM", ["groq", "openai"], index=0)
api_key = st.sidebar.text_input("🔑 Clé API", type="password", 
                                help="Groq: gsk_... | OpenAI: sk-...")
if api_key:
    st.session_state.api_key = api_key
    os.environ["API_KEY"] = api_key  # Pour compatibilité

# Modèle selon le fournisseur
MODELS = {
    "groq": "llama-3.3-70b-versatile",  # Gratuit, performant
    "openai": "gpt-4o-mini"  # Payant, très précis
}
MODEL = MODELS.get(provider, "llama-3.3-70b-versatile")

# Base URL selon le fournisseur
BASE_URLS = {
    "groq": "https://api.groq.com/openai/v1",
    "openai": "https://api.openai.com/v1"
}

# -----------------------------------------------------------------------------
# 🌤 OUTIL : Météo (Open-Meteo - Gratuit, sans clé)
# -----------------------------------------------------------------------------
def get_geocode(city):
    resp = requests.get(
        f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1&language=fr&format=json"
    )
    data = resp.json()
    if not data.get("results"):
        raise ValueError(f"Ville '{city}' introuvable.")
    return data["results"][0]

def get_weather(city, start_date, end_date):
    loc = get_geocode(city)
    lat, lon = loc["latitude"], loc["longitude"]
    url = (f"https://api.open-meteo.com/v1/forecast?"
           f"latitude={lat}&longitude={lon}"
           f"&daily=temperature_2m_max,temperature_2m_min,weathercode,precipitation_sum"
           f"&start_date={start_date}&end_date={end_date}&timezone=auto")
    resp = requests.get(url).json()
    daily = resp.get("daily", {})
    return {
        "city": city,
        "dates": daily.get("time", []),
        "temp_max": daily.get("temperature_2m_max", []),
        "temp_min": daily.get("temperature_2m_min", []),
        "weather_code": daily.get("weathercode", []),
        "precipitation": daily.get("precipitation_sum", [])
    }

def weather_code_to_desc(code):
    codes = {
        0: "☀️ Ensoleillé", 1: "🌤 Peu nuageux", 2: "⛅ Partiellement nuageux", 
        3: "☁️ Couvert", 45: "🌫 Brouillard", 51: "🌦 Bruine", 
        61: "🌧 Pluie légère", 71: "❄️ Neige", 80: "⛈ Averses", 95: "⚡ Orage"
    }
    return codes.get(code, "🌪 Conditions variables")

# -----------------------------------------------------------------------------
# 🤖 LLM WRAPPER (Groq + OpenAI compatibles)
# -----------------------------------------------------------------------------
def call_llm(messages, temperature=0.7, provider="groq"):
    """Appel LLM avec gestion d'erreurs et support multi-fournisseurs"""
    if not st.session_state.get("api_key"):
        return None
        
    try:
        client = openai.OpenAI(
            api_key=st.session_state.api_key,
            base_url=BASE_URLS.get(provider, "https://api.groq.com/openai/v1")
        )
        
        response = client.chat.completions.create(
            model=MODELS.get(provider, "llama-3.3-70b-versatile"),
            messages=messages,
            temperature=temperature,
            response_format={"type": "text"}
        )
        return response.choices[0].message.content.strip()
        
    except openai.RateLimitError:
        st.error("⚠️ Quota dépassé !")
        st.info("💡 Attendez quelques minutes ou vérifiez votre plan sur le dashboard du fournisseur.")
        return None
    except openai.AuthenticationError:
        st.error("🔑 Clé API invalide. Vérifiez-la dans la sidebar.")
        return None
    except Exception as e:
        st.error(f"❌ Erreur LLM: {type(e).__name__}: {str(e)[:150]}")
        return None

# -----------------------------------------------------------------------------
# 🧠 TECHNIQUE 1 : ReAct + Chain of Thought (CoT)
# -----------------------------------------------------------------------------
def react_cot_loop(initial_prompt, max_steps=4, provider="groq"):
    """
    Boucle ReAct avec CoT explicite :
    Thought: [raisonnement étape par étape]
    Action: [nom_outil]
    Action Input: {'json'}
    Observation: [résultat]
    """
    history = [{"role": "system", "content": initial_prompt}]
    steps = []
    
    for step in range(max_steps):
        # Prompt avec format strict (quotes simples pour éviter les erreurs f-string)
        prompt_text = (f"Étape {step+1}. Réponds STRICTEMENT au format:\n"
                      f"Thought: [ton raisonnement]\n"
                      f"Action: [get_weather ou autre]\n"
                      f"Action Input: {{'key': 'value'}}\n"
                      f"(ou Final Answer: [ta réponse] si terminé)")
        history.append({"role": "user", "content": prompt_text})
        
        response = call_llm(history, provider=provider)
        if not response:
            break
            
        history.append({"role": "assistant", "content": response})
        
        # Parsing des composants ReAct
        thought_match = re.search(r"Thought:\s*(.*?)(?:\nAction:|\nFinal Answer:|$)", response, re.DOTALL)
        action_match = re.search(r"Action:\s*(.*?)(?:\nAction Input:|\nFinal Answer:|$)", response, re.DOTALL)
        input_match = re.search(r"Action Input:\s*(.*?)(?:\nObservation:|\nFinal Answer:|$)", response, re.DOTALL)
        final_match = re.search(r"Final Answer:\s*(.*)", response, re.DOTALL)
        
        step_info = {
            "thought": thought_match.group(1).strip() if thought_match else "",
            "action": action_match.group(1).strip() if action_match else None
        }
        
        # Si réponse finale, on retourne
        if final_match:
            step_info["final"] = final_match.group(1).strip()
            steps.append(step_info)
            return step_info["final"], steps
            
        # Si action, on l'exécute
        if action_match and input_match:
            tool_name = action_match.group(1).strip()
            try:
                # Nettoyage et parsing JSON (support simple/double quotes)
                input_str = input_match.group(1).strip().replace("'", '"')
                tool_input = json.loads(input_str)
            except json.JSONDecodeError:
                tool_input = {"query": input_match.group(1).strip()}
                
            # Exécution de l'outil
            if tool_name == "get_weather":
                try:
                    obs = get_weather(
                        tool_input.get("city", ""),
                        tool_input.get("start_date", ""),
                        tool_input.get("end_date", "")
                    )
                    obs_str = json.dumps(obs, ensure_ascii=False, indent=2)
                except Exception as e:
                    obs_str = f"Erreur météo: {str(e)}"
            else:
                obs_str = f"Outil '{tool_name}' non implémenté."
                
            step_info["observation"] = obs_str
            history.append({"role": "user", "content": f"Observation: {obs_str}"})
        else:
            step_info["observation"] = "⚠️ Format invalide. Réessaie avec Thought/Action/Input."
            
        steps.append(step_info)
        
    return "⚠️ Limite d'étapes atteinte. Données partielles :", steps

# -----------------------------------------------------------------------------
# 🌳 TECHNIQUE 2 : Tree of Thoughts (ToT)
# -----------------------------------------------------------------------------
def tree_of_thoughts(weather_data, user_prefs, num_branches=3, provider="groq"):
    """Génère N pistes d'itinéraires, les évalue, garde la meilleure (élagage)"""
    
    # Génération des branches
    gen_prompt = f"""
    Tu es un expert en planification de voyage.
    Météo prévue pour {weather_data.get('city', 'la destination')}: 
    {json.dumps({k: v[:3] if isinstance(v, list) else v for k, v in weather_data.items()}, ensure_ascii=False, indent=2)}
    
    Préférences utilisateur: {user_prefs}
    
    Génère exactement {num_branches} propositions d'itinéraires concis.
    Format de retour STRICT (JSON valide uniquement):
    [
      {{"id": 1, "theme": "Nom du thème", "days": [{{"day": 1, "activity": "...", "reason": "adapté car..."}}, ...]}},
      ...
    ]
    """
    
    json_str = call_llm(
        [{"role": "system", "content": "Réponds UNIQUEMENT avec un tableau JSON valide, sans texte avant/après."},
         {"role": "user", "content": gen_prompt}],
        temperature=0.9,
        provider=provider
    )
    
    if not json_str:
        return {"id": 1, "theme": "Itinéraire par défaut", "days": []}, [], []
    
    # Nettoyage du JSON
    json_str = re.sub(r"```json\n?|```", "", json_str).strip()
    
    try:
        candidates = json.loads(json_str)
    except json.JSONDecodeError:
        # Fallback minimal
        return {"id": 1, "theme": "Itinéraire standard", "days": [{"day": 1, "activity": "Visite libre", "reason": "Flexible"}]}, [], []
    
    # Évaluation & élagage (ToT)
    eval_prompt = f"""
    Évalue ces {num_branches} propositions d'itinéraires sur 10 selon:
    1. Adaptation à la météo réelle
    2. Diversité des activités
    3. Réalisme logistique
    
    Retourne UNIQUEMENT ce JSON:
    [{{"id": x, "score": y, "raison": "court commentaire"}}, ...]
    """
    
    eval_json = call_llm(
        [{"role": "system", "content": "JSON uniquement, tableau de scores."},
         {"role": "user", "content": eval_prompt}],
        provider=provider
    )
    
    if eval_json:
        eval_json = re.sub(r"```json\n?|```", "", eval_json).strip()
        try:
            evaluations = json.loads(eval_json)
            best = max(evaluations, key=lambda x: x.get("score", 0))
            best_candidate = next((c for c in candidates if c["id"] == best["id"]), candidates[0])
            return best_candidate, candidates, evaluations
        except:
            pass
    
    return candidates[0] if candidates else {"days": []}, candidates, []

# -----------------------------------------------------------------------------
# 🔄 TECHNIQUE 3 : Self-Correction (Réflexion critique)
# -----------------------------------------------------------------------------
def self_correction(best_draft, weather_data, provider="groq"):
    """Critique le brouillon, détecte erreurs, régénère une version corrigée"""
    
    # Phase 1: Critique
    critique_prompt = f"""
    Itinéraire à critiquer: {json.dumps(best_draft, ensure_ascii=False, indent=2)}
    Météo réelle: {json.dumps(weather_data, ensure_ascii=False, indent=2)}
    
    Trouve 2-3 problèmes potentiels:
    - Activités incompatibles avec la météo (ex: plage sous la pluie)
    - Rythme trop dense ou logistique impossible
    - Oublis (repas, transports, réservations)
    
    Retourne UNIQUEMENT ce JSON:
    {{"critiques": ["problème 1", "..."], "suggestions": ["solution 1", "..."], "valide": true/false}}
    """
    
    critique_json = call_llm(
        [{"role": "system", "content": "JSON uniquement."},
         {"role": "user", "content": critique_prompt}],
        provider=provider
    )
    
    critique = {"critiques": [], "suggestions": [], "valide": True}
    if critique_json:
        critique_json = re.sub(r"```json\n?|```", "", critique_json).strip()
        try:
            critique = json.loads(critique_json)
        except:
            pass
    
    # Si valide, on garde le brouillon
    if critique.get("valide", True) and not critique.get("critiques"):
        return best_draft, critique
    
    # Phase 2: Régénération corrigée
    fix_prompt = f"""
    Itinéraire initial: {json.dumps(best_draft, ensure_ascii=False, indent=2)}
    Critiques reçues: {json.dumps(critique, ensure_ascii=False, indent=2)}
    Météo à respecter: {json.dumps(weather_data, ensure_ascii=False, indent=2)}
    
    Réécris l'itinéraire FINAL en corrigeant TOUTES les critiques.
    Format JSON STRICT:
    {{
      "city": "nom ville",
      "duration_days": 3,
      "itinerary": [
        {{"day": 1, "weather": "description", "morning": "...", "afternoon": "...", "evening": "...", "transport": "...", "notes": "..."}},
        ...
      ]
    }}
    """
    
    final_json = call_llm(
        [{"role": "system", "content": "JSON valide uniquement, pas de texte supplémentaire."},
         {"role": "user", "content": fix_prompt}],
        temperature=0.3,  # Plus déterministe pour la correction
        provider=provider
    )
    
    if final_json:
        final_json = re.sub(r"```json\n?|```", "", final_json).strip()
        try:
            return json.loads(final_json), critique
        except:
            pass
    
    # Fallback: retourne le brouillon original
    return best_draft, critique

# -----------------------------------------------------------------------------
# 🧩 ORCHESTRATION PRINCIPALE
# -----------------------------------------------------------------------------
def run_travel_agent(user_input, provider="groq"):
    """Pipeline complet : ReAct → ToT → Self-Correction → Résultat"""
    
    if not st.session_state.get("api_key"):
        return "⚠️ Veuillez entrer votre clé API dans la barre latérale.", None, None
    
    # Extraction basique des paramètres (à améliorer avec NLP)
    city = "Paris"
    city_match = re.search(r"(?:à|pour|vers|depuis)\s+([A-Za-zÀ-ÿ\s]+?)(?:\s+(?:du|le|\d)|$)", user_input)
    if city_match:
        city = city_match.group(1).strip()
    
    # Dates par défaut : aujourd'hui + 4 jours
    today = datetime.now()
    start_date = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    end_date = (today + timedelta(days=5)).strftime("%Y-%m-%d")
    
    date_match = re.search(r"(\d{1,2})[/-](\d{1,2})", user_input)
    if date_match:
        d, m = date_match.groups()
        start_date = f"{today.year}-{m.zfill(2)}-{d.zfill(2)}"
        end_date = (datetime.strptime(start_date, "%Y-%m-%d") + timedelta(days=4)).strftime("%Y-%m-%d")
    
    prefs = re.sub(r"(?:planifie|voyage|destination|météo|activité).*", "", user_input, flags=re.IGNORECASE).strip()
    if not prefs or len(prefs) < 10:
        prefs = "Culture, nature, gastronomie, détente"
    
    # 1️⃣ ReAct + CoT : Collecte météo
    st.info("🔍 Étape 1/4: ReAct + Chain of Thought (collecte données)")
    react_prompt = f"""
    Tu es un agent de voyage. Ta première tâche : récupérer la météo de {city} 
    du {start_date} au {end_date} pour adapter les activités.
    
    Utilise l'outil 'get_weather' avec ce format exact:
    Thought: [analyse de la demande]
    Action: get_weather
    Action Input: {{"city": "{city}", "start_date": "{start_date}", "end_date": "{end_date}"}}
    """
    
    collected_data, react_steps = react_cot_loop(react_prompt, provider=provider)
    
    # Extraction des données météo depuis les steps
    weather_data = None
    for step in react_steps:
        obs = step.get("observation", "")
        try:
            data = json.loads(obs) if obs.startswith("{") else None
            if data and "city" in data:
                weather_data = data
                break
        except:
            continue
    
    if not weather_data:
        # Fallback météo simulée pour démo
        weather_data = {
            "city": city, "dates": [start_date],
            "temp_max": [20, 22, 19, 21, 23],
            "weather_code": [1, 2, 61, 2, 0],
            "precipitation": [0, 0, 5, 0, 0]
        }
        st.warning("⚠️ Météo simulée (API indisponible)")
    
    # 2️⃣ Tree of Thoughts : Génération & sélection
    st.info("🌳 Étape 2/4: Tree of Thoughts (génération de pistes)")
    best_draft, branches, evaluations = tree_of_thoughts(weather_data, prefs, provider=provider)
    
    # 3️⃣ Self-Correction : Critique & amélioration
    st.info("🔄 Étape 3/4: Self-Correction (vérification qualité)")
    final_itinerary, critique = self_correction(best_draft, weather_data, provider=provider)
    
    # 4️⃣ Formatage
    st.success("✅ Étape 4/4: Itinéraire finalisé")
    
    reasoning_trace = {
        "react_steps": react_steps,
        "tot_evaluations": evaluations,
        "self_correction": critique
    }
    
    return f"🎉 Itinéraire prêt pour {city} !", final_itinerary, reasoning_trace

# -----------------------------------------------------------------------------
# 💻 INTERFACE STREAMLIT
# -----------------------------------------------------------------------------
st.title("🌍 Planificateur de Voyage Autonome")
st.caption("Agent LLM avec ReAct • Chain of Thought • Tree of Thoughts • Self-Correction")

# Initialisation session
if "conversation" not in st.session_state:
    st.session_state.conversation = []
if "current_itinerary" not in st.session_state:
    st.session_state.current_itinerary = None

# Affichage historique chat
for msg in st.session_state.conversation:
    with st.chat_message(msg["role"]):
        if msg.get("itinerary_preview"):
            st.markdown("### 🗺️ Aperçu itinéraire")
            for day in msg["itinerary_preview"].get("itinerary", [])[:2]:  # Aperçu 2 premiers jours
                st.markdown(f"**Jour {day.get('day')}** | {day.get('weather', '')}")
                st.markdown(f"- 🌅 {day.get('morning', '')}")
        if msg.get("content"):
            st.markdown(msg["content"])

# Zone de saisie
placeholder = "Ex: Planifie un week-end à Bordeaux du 15-06, j'aime le vin et l'architecture"
if prompt := st.chat_input(placeholder):
    # Message utilisateur
    st.session_state.conversation.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Réponse agent
    with st.chat_message("assistant"):
        with st.spinner("🤖 Agent en réflexion (ReAct → ToT → Correction)..."):
            response_text, itinerary, reasoning = run_travel_agent(prompt, provider=provider)
            
            st.markdown(response_text)
            
            # Affichage raisonnement (collapsible)
            if reasoning and st.checkbox("🔍 Voir le raisonnement détaillé", value=False):
                with st.expander("🧠 Traces de raisonnement"):
                    st.markdown("#### 📝 ReAct + CoT")
                    for i, step in enumerate(reasoning.get("react_steps", [])):
                        st.markdown(f"**Étape {i+1}**: `{step.get('thought', '')[:100]}...`")
                        if step.get("observation"):
                            st.code(step["observation"][:200] + "...", language="json")
                    
                    st.markdown("#### 🌳 Tree of Thoughts")
                    if reasoning.get("tot_evaluations"):
                        st.json(reasoning["tot_evaluations"])
                    
                    st.markdown("#### 🔄 Self-Correction")
                    st.json(reasoning.get("self_correction", {}))
            
            # Affichage itinéraire complet
            if itinerary and itinerary.get("itinerary"):
                st.markdown("### 📅 Itinéraire jour par jour")
                for day in itinerary["itinerary"]:
                    with st.container(border=True):
                        st.markdown(f"**Jour {day.get('day')}** | {day.get('weather', 'Météo inconnue')}")
                        col1, col2, col3 = st.columns(3)
                        with col1: st.markdown(f"🌅 **Matin**\n\n{day.get('morning', '-')}")
                        with col2: st.markdown(f"☀️ **Après-midi**\n\n{day.get('afternoon', '-')}")
                        with col3: st.markdown(f"🌙 **Soirée**\n\n{day.get('evening', '-')}")
                        if day.get("notes"):
                            st.caption(f"📌 {day.get('notes')}")
                
                # Bouton téléchargement
                md_content = f"# 🗺️ Itinéraire : {itinerary.get('city', 'Voyage')}\n\n"
                for d in itinerary["itinerary"]:
                    md_content += f"## Jour {d.get('day')} | {d.get('weather', '')}\n"
                    md_content += f"- 🌅 Matin: {d.get('morning', '')}\n"
                    md_content += f"- ☀️ Après-midi: {d.get('afternoon', '')}\n"
                    md_content += f"- 🌙 Soirée: {d.get('evening', '')}\n"
                    if d.get("notes"): md_content += f"- 📌 {d.get('notes')}\n"
                    md_content += "\n"
                
                st.download_button(
                    "📥 Télécharger l'itinéraire (.md)",
                    data=md_content,
                    file_name=f"itineraire_{itinerary.get('city', 'voyage')}.md",
                    mime="text/markdown"
                )
                
                # Sauvegarde dans l'historique
                st.session_state.current_itinerary = itinerary
            
            # Sauvegarde conversation
            st.session_state.conversation.append({
                "role": "assistant",
                "content": response_text,
                "itinerary_preview": itinerary
            })

# Footer
st.sidebar.markdown("---")
st.sidebar.caption("💡 **Astuce** : Groq = gratuit & rapide. Pour OpenAI, ajoutez un moyen de paiement sur platform.openai.com")
st.sidebar.markdown("[📚 Docs techniques](https://docs.streamlit.io) | [🐛 Signaler un bug]")