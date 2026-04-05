import re
import json
from llm import call_llm
from tools import get_weather, search_flights

def react_cot_loop(system_prompt, user_input, max_steps=4, provider="groq"):
    """
    ReAct + Chain of Thought :
    Thought -> Action (outil) -> Observation -> ... -> Final Answer
    """
    history = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Demande utilisateur : {user_input}"}
    ]
    steps = []
    for step in range(max_steps):
        prompt_line = (
            f"Étape {step+1}. Réponds STRICTEMENT au format :\n"
            "Thought: [ton analyse étape par étape]\n"
            "Action: [get_weather ou search_flights ou none]\n"
            "Action Input: {'param': 'valeur'}\n"
            "(ou Final Answer: [réponse JSON ou texte] si terminé)"
        )
        history.append({"role": "user", "content": prompt_line})
        response = call_llm(history, provider=provider)
        if not response:
            break
        history.append({"role": "assistant", "content": response})

        thought = re.search(r"Thought:\s*(.*?)(?:\nAction:|\nFinal Answer:|$)", response, re.DOTALL)
        action = re.search(r"Action:\s*(.*?)(?:\nAction Input:|\nFinal Answer:|$)", response, re.DOTALL)
        inp = re.search(r"Action Input:\s*(.*?)(?:\nObservation:|\nFinal Answer:|$)", response, re.DOTALL)
        final = re.search(r"Final Answer:\s*(.*)", response, re.DOTALL)

        step_data = {
            "thought": thought.group(1).strip() if thought else "",
            "action": action.group(1).strip() if action else None
        }

        if final:
            step_data["final"] = final.group(1).strip()
            steps.append(step_data)
            return step_data["final"], steps

        if action and inp:
            tool = action.group(1).strip()
            try:
                params = json.loads(inp.group(1).strip().replace("'", '"'))
            except:
                params = {"raw": inp.group(1).strip()}

            if tool == "get_weather":
                obs = get_weather(
                    params.get("city", "Paris"),
                    params.get("start_date", ""),
                    params.get("end_date", "")
                )
            elif tool == "search_flights":
                obs = search_flights(
                    params.get("origin", "Paris"),
                    params.get("destination", ""),
                    params.get("date", ""),
                    params.get("return_date"),
                    params.get("cabin", "economy")
                )
            elif tool.lower() == "none":
                obs = {"info": "Aucune action exécutée à cette étape."}
            else:
                obs = {"error": f"Outil '{tool}' inconnu. Utilise: get_weather, search_flights, none."}

            step_data["observation"] = json.dumps(obs, ensure_ascii=False, indent=2)
            history.append({"role": "user", "content": f"Observation: {step_data['observation']}"})
        else:
            step_data["observation"] = "⚠️ Format invalide. Réessaie."
        steps.append(step_data)

    return "⚠️ Limite d'étapes atteinte.", steps


def tree_of_thoughts(weather, prefs, provider="groq"):
    """
    Tree of Thoughts :
    - Génère plusieurs itinéraires candidats
    - Les évalue
    - Sélectionne le meilleur
    Format final aligné avec l'UI : city + itinerary[day, weather, morning, afternoon, evening, notes]
    """
    prompt = f"""
Météo (JSON): {json.dumps(weather, ensure_ascii=False)}
Préférences utilisateur: {prefs}

1) Propose EXACTEMENT 3 itinéraires candidats en JSON strict.
2) Chaque candidat doit avoir la forme:
{{
  "id": 1,
  "city": "{weather.get('city','')}",
  "itinerary": [
    {{"day": 1, "weather": "☀️ 22°C", "morning": "activité matin", "afternoon": "activité après-midi", "evening": "activité soirée", "notes": ""}}
  ]
}}

Retourne uniquement:
[
  {{ "id": 1, "city": "...", "itinerary": [...] }},
  {{ "id": 2, ... }},
  {{ "id": 3, ... }}
]
"""
    raw = call_llm(
        [
            {"role": "system", "content": "Tu es un planificateur de voyage. Réponds en JSON strict uniquement."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.9,
        provider=provider,
    )
    if not raw:
        return {"city": weather.get("city", ""), "itinerary": []}, [], []

    try:
        candidates = json.loads(re.sub(r"```json\n?|```", "", raw).strip())
    except:
        return {"city": weather.get("city", ""), "itinerary": []}, [], []

    eval_prompt = f"""
Évalue ces {len(candidates)} itinéraires sur 10 selon:
- adéquation à la météo
- réalisme
- diversité des activités

Retourne JSON strict:
[{{"id": 1, "score": 0-10}}, ...]
Candidats: {json.dumps(candidates, ensure_ascii=False)}
"""
    eval_raw = call_llm(
        [
            {"role": "system", "content": "JSON uniquement."},
            {"role": "user", "content": eval_prompt},
        ],
        provider=provider,
    )
    try:
        scores = json.loads(re.sub(r"```json\n?|```", "", eval_raw).strip())
        best = max(scores, key=lambda x: x.get("score", 0))
        best_candidate = next((c for c in candidates if c["id"] == best["id"]), candidates[0])
        return best_candidate, candidates, scores
    except:
        return candidates[0], candidates, []


def self_correction(draft, weather, provider="groq"):
    """
    Self-Correction :
    - critique l'itinéraire
    - corrige si nécessaire
    """
    crit_prompt = f"""
Analyse cet itinéraire de voyage (JSON): {json.dumps(draft, ensure_ascii=False)}
Météo prévue (JSON): {json.dumps(weather, ensure_ascii=False)}

1) Détecte les incohérences (météo, rythme, logique, réalisme).
2) Propose des critiques ciblées.

Retourne JSON strict:
{{"critiques": ["...","..."], "valide": true/false}}
"""
    crit_raw = call_llm(
        [
            {"role": "system", "content": "Tu es un critique de plans de voyage. Réponds en JSON uniquement."},
            {"role": "user", "content": crit_prompt},
        ],
        provider=provider,
    )
    critique = {"critiques": [], "valide": True}
    try:
        critique = json.loads(re.sub(r"```json\n?|```", "", crit_raw).strip())
    except:
        pass

    if critique.get("valide") and not critique.get("critiques"):
        return draft, critique

    fix_prompt = f"""
Corrige cet itinéraire en tenant compte des critiques suivantes:
{json.dumps(critique, ensure_ascii=False)}

Météo:
{json.dumps(weather, ensure_ascii=False)}

Retourne un JSON STRICT au format:
{{
  "city": "{draft.get('city','')}",
  "itinerary": [
    {{"day": 1, "weather": "☀️ 22°C", "morning": "activité matin", "afternoon": "activité après-midi", "evening": "activité soirée", "notes": ""}}
  ]
}}

Itinéraire initial:
{json.dumps(draft, ensure_ascii=False)}
"""
    fix_raw = call_llm(
        [
            {"role": "system", "content": "Tu es un planificateur de voyage. Réponds en JSON strict uniquement."},
            {"role": "user", "content": fix_prompt},
        ],
        temperature=0.3,
        provider=provider,
    )
    try:
        return json.loads(re.sub(r"```json\n?|```", "", fix_raw).strip()), critique
    except:
        return draft, critique
