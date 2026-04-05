import streamlit as st
from config import MODELS
from orchestrator import run_agent

st.set_page_config(page_title="🌍 Planificateur de Voyage Autonome", layout="wide")

st.sidebar.title("⚙️ Configuration")
provider = st.sidebar.selectbox("🔌 Fournisseur LLM", ["groq", "openai"], index=0)
api_key = st.sidebar.text_input("🔑 Clé API", type="password", help="Groq: gsk_... | OpenAI: sk-...")
if api_key:
    st.session_state.api_key = api_key

st.title("🌍 Planificateur de Voyage Autonome")
st.caption("ReAct • CoT • Tree of Thoughts • Self-Correction • Multi-Outils")

if "msgs" not in st.session_state:
    st.session_state.msgs = []
if "last_data" not in st.session_state:
    st.session_state.last_data = None

# Historique
for m in st.session_state.msgs:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Ex: Planifie-moi un voyage à Lisbonne en juin avec beaucoup de culture")
if prompt:
    st.session_state.msgs.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("🤔 Agent en réflexion..."):
            txt, data, trace = run_agent(prompt, provider=provider)
            st.markdown(txt)
            
            # Affichage Raisonnement (ReAct)
            if trace:
                with st.expander("🧠 Traces de raisonnement", expanded=False):
                    for i, s in enumerate(trace.get("react_steps", []), 1):
                        st.markdown(f"**Étape {i}** 🧠 `{s.get('thought','')[:80]}...`")
                        if s.get("observation"):
                            st.code(s["observation"][:150] + "...", "json")
            
            st.session_state.last_data = data

            # Affichage des résultats
            if data and isinstance(data, dict):
                # VOLS
                if data.get("outbound"):
                    st.markdown("### ✈️ Vols trouvés")
                    tabs = st.tabs(["🛫 Aller"] + (["🔁 Retour"] if data.get("return") else []))
                    for idx, leg in enumerate([data["outbound"], data.get("return", [])]):
                        if not leg:
                            continue
                        with tabs[idx]:
                            for i, f in enumerate(leg, 1):
                                with st.container(border=True):
                                    c1, c2, c3 = st.columns([2, 2, 1])
                                    with c1:
                                        st.markdown(f"**{f['airline']}** | `{f['flight']}`")
                                        st.caption(f"{f['departure']} → {f['arrival']} • {f['duration']}")
                                        st.success("✅ Direct" if f["stops"] == 0 else f"🔁 {f['stops']} escale")
                                    with c2:
                                        st.markdown(f"🎫 {f['cabin'].title()}")
                                    with c3:
                                        st.metric("Prix", f"{f['price']} {f['currency']}")
                    st.caption(data.get("note", ""))
                
                # ITINÉRAIRE
                elif data.get("itinerary"):
                    st.markdown("### 📅 Itinéraire jour par jour")
                    for d in data["itinerary"]:
                        with st.container(border=True):
                            st.markdown(f"**Jour {d.get('day')}** | {d.get('weather','')}")
                            c1, c2, c3 = st.columns(3)
                            with c1:
                                st.markdown(f"🌅 **Matin**\n{d.get('morning','')}")
                            with c2:
                                st.markdown(f"☀️ **Après-midi**\n{d.get('afternoon','')}")
                            with c3:
                                st.markdown(f"🌙 **Soirée**\n{d.get('evening','')}")
                            if d.get("notes"):
                                st.caption(f"📌 {d['notes']}")
                    
                    md = f"# 🗺️ Itinéraire : {data.get('city','Voyage')}\n"
                    for d in data["itinerary"]:
                        md += (
                            f"\n## Jour {d.get('day')}\n"
                            f"- Météo: {d.get('weather')}\n"
                            f"- Matin: {d.get('morning')}\n"
                            f"- Après-midi: {d.get('afternoon')}\n"
                            f"- Soirée: {d.get('evening')}\n"
                        )
                    st.download_button(
                        "📥 Télécharger (.md)",
                        md,
                        file_name="itineraire.md",
                        mime="text/markdown"
                    )
                else:
                    st.json(data)
                    
            st.session_state.msgs.append({"role": "assistant", "content": txt})

st.sidebar.markdown("---")
st.sidebar.caption("💡 Groq = gratuit & rapide. OpenAI = payant.")
