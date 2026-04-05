import re
import json
from llm import call_llm
from tools import get_weather, search_flights

def react_cot_loop(system_prompt, max_steps=4, provider="groq"):
    history = [{"role": "system", "content": system_prompt}]
    steps = []
    for step in range(max_steps):
        prompt_line = (f"Étape {step+1}. Réponds STRICTEMENT au format:\n"
                       "Thought: [ton analyse étape par étape]\n"
                       "Action: [get_weather ou search_flights]\n"
                       "Action Input: {'param': 'valeur'}\n"
                       "(ou Final Answer: [réponse JSON ou texte] si terminé)")
        history.append({"role": "user", "content": prompt_line})
        response = call_llm(history, provider=provider)
        if not response: break
        history.append({"role": "assistant", "content": response})

        thought = re.search(r"Thought:\s*(.*?)(?:\nAction:|\nFinal Answer:|$)", response, re.DOTALL)
        action = re.search(r"Action:\s*(.*?)(?:\nAction Input:|\nFinal Answer:|$)", response, re.DOTALL)
        inp = re.search(r"Action Input:\s*(.*?)(?:\nObservation:|\nFinal Answer:|$)", response, re.DOTALL)
        final = re.search(r"Final Answer:\s*(.*)", response, re.DOTALL)

        step_data = {"thought": thought.group(1).strip() if thought else "", "action": action.group(1).strip() if action else None}

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
                obs = get_weather(params.get("city", "Paris"), params.get("start_date", ""), params.get("end_date", ""))
            elif tool == "search_flights":
                obs = search_flights(params.get("origin", "Paris"), params.get("destination", ""), params.get("date", ""), params.get("return_date"), params.get("cabin", "economy"))
            else:
                obs = {"error": f"Outil '{tool}' inconnu. Utilise: get_weather, search_flights"}

            step_data["observation"] = json.dumps(obs, ensure_ascii=False, indent=2)
            history.append({"role": "user", "content": f"Observation: {step_data['observation']}"})
        else:
            step_data["observation"] = "⚠️ Format invalide. Réessaie."
        steps.append(step_data)
    return "⚠️ Limite d'étapes atteinte.", steps

def tree_of_thoughts(weather, prefs, provider="groq"):
    prompt = f"""Météo: {json.dumps(weather, ensure_ascii=False)}\nPréférences: {prefs}\nGénère EXACTEMENT 3 propositions d'itinéraires en JSON strict:\n[{{"id":1, "theme":"Nom", "days":[{{"day":1, "activity":"...","reason":"..."}}]}}]"""
    raw = call_llm([{"role":"system","content":"JSON uniquement."},{"role":"user","content":prompt}], 0.9, provider)
    if not raw: return {"days":[]}, [], []
    try:
        candidates = json.loads(re.sub(r"```json\n?|```", "", raw).strip())
    except: return {"days":[]}, [], []
    
    eval_prompt = f"Évalue ces {len(candidates)} options sur 10 (météo, réalisme, diversité). Retourne JSON: [{{'id':x, 'score':y}}]"
    eval_raw = call_llm([{"role":"system","content":"JSON uniquement."},{"role":"user","content":eval_prompt}], provider=provider)
    try:
        scores = json.loads(re.sub(r"```json\n?|```", "", eval_raw).strip())
        best = max(scores, key=lambda x: x.get("score", 0))
        return next((c for c in candidates if c["id"]==best["id"]), candidates[0]), candidates, scores
    except: return candidates[0], candidates, []

def self_correction(draft, weather, provider="groq"):
    crit_prompt = f"Analyse: {json.dumps(draft, ensure_ascii=False)}\nMétéo: {json.dumps(weather, ensure_ascii=False)}\nRetourne JSON: {{'critiques':[], 'valide':bool}}"
    crit_raw = call_llm([{"role":"system","content":"JSON uniquement."},{"role":"user","content":crit_prompt}], provider=provider)
    critique = {"critiques":[], "valide":True}
    try: critique = json.loads(re.sub(r"```json\n?|```", "", crit_raw).strip())
    except: pass
    
    if critique.get("valide") and not critique.get("critiques"): return draft, critique
    
    fix_prompt = f"Corrige cet itinéraire en tenant compte des critiques: {json.dumps(critique)}\nMétéo: {json.dumps(weather)}\nRetourne JSON strict: {{'city':'', 'itinerary':[{{'day':1, 'weather':'', 'morning':'', 'afternoon':'', 'evening':'', 'notes':''}}]}}"
    fix_raw = call_llm([{"role":"system","content":"JSON uniquement."},{"role":"user","content":fix_prompt}], 0.3, provider)
    try: return json.loads(re.sub(r"```json\n?|```", "", fix_raw).strip()), critique
    except: return draft, critique