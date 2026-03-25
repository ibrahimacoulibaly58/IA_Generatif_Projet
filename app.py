import streamlit as st
from agent import run_agent

st.set_page_config(page_title="✈️ Travel Planner AI", layout="wide")

st.title("✈️ Planificateur de Voyage Intelligent")
st.markdown("Application basée sur des agents IA (ReAct + Multi-Agents + Tree of Thoughts)")

# INPUTS
col1, col2 = st.columns(2)

with col1:
    destination = st.text_input("🌍 Destination")

with col2:
    days = st.slider("📅 Nombre de jours", 1, 10, 3)

# ACTION
if st.button("🚀 Générer mon voyage"):
    if destination:

        with st.spinner("🤖 Les agents réfléchissent..."):
            # Appel à l'agent principal
            result = run_agent(destination, days)

        st.success(f"Voyage généré pour {destination} sur {days} jours ✅")

        # LLM utilisé
        st.info("💬 LLM utilisé : LLaMA 3.1 via Groq")

        # Résumé du plan
        if "summary" in result:
            st.subheader("📝 Résumé du voyage")
            st.write(result["summary"])

        # Raisonnement détaillé
        if "steps" in result:
            with st.expander("🧠 Voir le raisonnement étape par étape"):
                for step, content in result["steps"]:
                    st.markdown(f"### {step}")
                    st.write(content)

        # Affichage des alternatives (Tree of Thoughts)
        if "alternatives" in result:
            with st.expander("🌳 Alternatives proposées"):
                for alt in result["alternatives"]:
                    st.write(alt)

        # Résultats principaux
        st.subheader("🌤️ Météo")
        st.info(result.get("weather", "Météo non disponible"))

        st.subheader("🎯 Activités")
        st.write(result.get("activities", "Aucune activité générée"))

        st.subheader("🧐 Auto-critique (Agent 2)")
        st.write(result.get("critique", "Pas de critique disponible"))

        st.subheader("🗺️ Itinéraire final")
        st.write(result.get("itinerary", "Aucun itinéraire généré"))

        # téléchargement
        st.download_button(
            label="📥 Télécharger le plan",
            data=result.get("itinerary", ""),
            file_name=f"voyage_{destination}.txt"
        )

    else:
        st.warning("⚠️ Entre une destination")