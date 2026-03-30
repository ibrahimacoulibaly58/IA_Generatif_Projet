import streamlit as st
from agent import (
    run_full_workflow,
    stream_profile,
    stream_itinerary,
    stream_transport,
    stream_hotel,
    export_agent,
    email_agent
)
from utils import (
    init_session_state,
    reset_session,
    next_step,
    prev_step,
    display_step_indicator,
    display_agent_thinking,
    generate_pdf,
    create_download_button,
    send_email_simulation,
    prepare_email_content
)

# ============================================================
# 🎨 CONFIGURATION DE LA PAGE
# ============================================================
st.set_page_config(
    page_title="✈️ Travel Planner AI",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# 🎯 INITIALISATION SESSION STATE
# ============================================================
init_session_state()

# ============================================================
# 🎨 SIDEBAR - INFORMATIONS & NAVIGATION
# ============================================================
with st.sidebar:
    st.title("🌍 Travel Planner AI")
    st.markdown("---")
    
    # Navigation rapide
    st.subheader("📍 Navigation")
    if st.button("🔄 Nouveau voyage", use_container_width=True, key="new_trip_sidebar"):
        reset_session()
        st.rerun()
    
    if st.session_state.step > 1:
        if st.button("⬅️ Étape précédente", use_container_width=True, key="prev_step_sidebar"):
            prev_step()
            st.rerun()
    
    st.markdown("---")
    
    # Informations voyageur
    st.subheader("👤 Voyageur")
    st.session_state.user_name = st.text_input(
        "Nom",
        value=st.session_state.user_name,
        placeholder="Votre nom",
        key="user_name_sidebar"
    )
    st.session_state.user_email = st.text_input(
        "Email",
        value=st.session_state.user_email,
        placeholder="votre@email.com",
        key="user_email_sidebar"
    )
    
    st.markdown("---")
    
    # Infos techniques
    st.subheader("ℹ️ Info")
    st.markdown("""
    - **LLM** : LLaMA 3.1 via Groq
    - **Agents** : 6 agents spécialisés
    - **Streaming** : Oui
    """)

# ============================================================
# 🎯 CONTENU PRINCIPAL
# ============================================================
st.title("✈️ Planificateur de Voyage Intelligent")
st.markdown("### Créez votre voyage sur mesure avec l'IA 🤖")

# Barre de progression des étapes
display_step_indicator(st.session_state.step)
st.markdown("---")

# ============================================================
# 📋 ÉTAPE 1 : INFORMATIONS DE VOYAGE
# ============================================================
if st.session_state.step == 1:
    st.header("📋 Étape 1 : Informations de voyage")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.destination = st.text_input(
            "🌍 Destination",
            value=st.session_state.destination,
            placeholder="Ex: Paris, Tokyo, New York...",
            key="destination_step1"
        )
        st.session_state.origin = st.text_input(
            "🛫 Lieu de départ",
            value=st.session_state.origin,
            placeholder="Ex: France, Paris, Lyon...",
            key="origin_step1"
        )
    
    with col2:
        col_date1, col_date2 = st.columns(2)
        with col_date1:
            st.session_state.start_date = st.date_input(
                "📅 Date de départ",
                value=st.session_state.start_date,
                key="start_date_step1"
            )
        with col_date2:
            st.session_state.end_date = st.date_input(
                "📅 Date de retour",
                value=st.session_state.end_date,
                key="end_date_step1"
            )
    
    st.session_state.interests = st.text_area(
        "🎯 Centres d'intérêt (optionnel)",
        value=st.session_state.interests,
        placeholder="Ex: culture, gastronomie, aventure...",
        height=100,
        key="interests_step1"
    )
    
    st.session_state.budget = st.select_slider(
        "💰 Budget hébergement",
        options=["économique", "moyen", "confort", "luxe"],
        value=st.session_state.budget or "moyen",
        key="budget_step1"
    )
    
    st.markdown("---")
    
    col_btn1, col_btn2 = st.columns([3, 1])
    with col_btn1:
        if st.button("🚀 Générer mon voyage", type="primary", use_container_width=True, key="generate_trip"):
            if not st.session_state.destination:
                st.error("⚠️ Veuillez entrer une destination")
            elif not st.session_state.start_date or not st.session_state.end_date:
                st.error("⚠️ Veuillez sélectionner les dates")
            elif st.session_state.start_date > st.session_state.end_date:
                st.error("⚠️ La date de retour doit être après la date de départ")
            else:
                next_step()
                st.rerun()
    with col_btn2:
        st.info(f"Étape {st.session_state.step}/5")

# ============================================================
# 🗺️ ÉTAPE 2 : CHOIX DE L'ITINÉRAIRE
# ============================================================
elif st.session_state.step == 2:
    st.header("🗺️ Étape 2 : Choisissez votre itinéraire")
    
    if not st.session_state.itinerary_option_a:
        with st.spinner("🤖 Les agents préparent vos options..."):
            with st.expander("📝 Génération Option A", expanded=False):
                response_a = ""
                placeholder_a = st.empty()
                for chunk in stream_itinerary(
                    st.session_state.destination,
                    st.session_state.start_date,
                    st.session_state.end_date,
                    st.session_state.interests,
                    option_number=1
                ):
                    response_a += chunk
                    placeholder_a.markdown(response_a + "▌")
                st.session_state.itinerary_option_a = response_a
            
            with st.expander("📝 Génération Option B", expanded=False):
                response_b = ""
                placeholder_b = st.empty()
                for chunk in stream_itinerary(
                    st.session_state.destination,
                    st.session_state.start_date,
                    st.session_state.end_date,
                    st.session_state.interests,
                    option_number=2
                ):
                    response_b += chunk
                    placeholder_b.markdown(response_b + "▌")
                st.session_state.itinerary_option_b = response_b
            
            st.session_state.comparison = "✅ Deux options générées avec succès"
            st.session_state.profile_generated = True
        
        st.success("✅ Itinéraires générés !")
        st.rerun()
    
    st.markdown("### 📊 Comparez les 2 options")
    if st.session_state.comparison:
        st.info(f"📝 {st.session_state.comparison}")
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("#### 🅰️ Option A")
        st.markdown(st.session_state.itinerary_option_a)
        if st.button("✅ Choisir l'Option A", type="primary", use_container_width=True, key="choose_option_a"):
            st.session_state.selected_option = "A"
            next_step()
            st.rerun()
    
    with col_b:
        st.markdown("#### 🅱️ Option B")
        st.markdown(st.session_state.itinerary_option_b)
        if st.button("✅ Choisir l'Option B", type="primary", use_container_width=True, key="choose_option_b"):
            st.session_state.selected_option = "B"
            next_step()
            st.rerun()
    
    if st.button("🔄 Régénérer les options", key="regenerate_options"):
        st.session_state.itinerary_option_a = None
        st.session_state.itinerary_option_b = None
        st.session_state.comparison = None
        st.rerun()

# ============================================================
# 🚄 ÉTAPE 3 : TRANSPORT
# ============================================================
elif st.session_state.step == 3:
    st.header("🚄 Étape 3 : Options de transport")
    
    if not st.session_state.transport_content:
        with st.spinner("🤖 L'agent transport recherche les meilleures options..."):
            response = ""
            placeholder = st.empty()
            for chunk in stream_transport(
                st.session_state.destination,
                st.session_state.start_date,
                st.session_state.end_date,
                st.session_state.origin
            ):
                response += chunk
                placeholder.markdown(response + "▌")
            st.session_state.transport_content = response
            st.session_state.transport_generated = True
        st.success("✅ Options de transport générées !")
        st.rerun()
    
    st.markdown(st.session_state.transport_content)
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("💡 **Conseil** : Cliquez sur les liens pour réserver directement")
    with col2:
        if st.button("✅ Valider & Continuer", type="primary", use_container_width=True, key="validate_transport"):
            next_step()
            st.rerun()
    
    if st.button("🔄 Régénérer", key="regenerate_transport"):
        st.session_state.transport_content = None
        st.session_state.transport_generated = False
        st.rerun()

# ============================================================
# 🏨 ÉTAPE 4 : HÉBERGEMENT
# ============================================================
elif st.session_state.step == 4:
    st.header("🏨 Étape 4 : Options d'hébergement")
    
    if not st.session_state.hotel_content:
        with st.spinner("🤖 L'agent hôtel trouve les meilleurs quartiers..."):
            response = ""
            placeholder = st.empty()
            for chunk in stream_hotel(
                st.session_state.destination,
                st.session_state.start_date,
                st.session_state.end_date,
                st.session_state.budget
            ):
                response += chunk
                placeholder.markdown(response + "▌")
            st.session_state.hotel_content = response
            st.session_state.hotel_generated = True
        st.success("✅ Options d'hébergement générées !")
        st.rerun()
    
    st.markdown(st.session_state.hotel_content)
    st.markdown("---")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("💡 **Conseil** : Réservez tôt pour les meilleurs prix")
    with col2:
        if st.button("✅ Valider & Continuer", type="primary", use_container_width=True, key="validate_hotel"):
            next_step()
            st.rerun()
    
    if st.button("🔄 Régénérer", key="regenerate_hotel"):
        st.session_state.hotel_content = None
        st.session_state.hotel_generated = False
        st.rerun()

# ============================================================
# 📤 ÉTAPE 5 : EXPORT & CONFIRMATION
# ============================================================
elif st.session_state.step == 5:
    st.header("📤 Étape 5 : Export et confirmation")
    
    if not st.session_state.export_content:
        with st.spinner("🤖 Préparation de votre document de voyage..."):
            selected_itinerary = (
                st.session_state.itinerary_option_a 
                if st.session_state.selected_option == "A" 
                else st.session_state.itinerary_option_b
            )
            st.session_state.export_content = export_agent(
                st.session_state.destination,
                selected_itinerary,
                st.session_state.transport_content,
                st.session_state.hotel_content,
                st.session_state.user_name,
                st.session_state.user_email
            )
            st.session_state.email_content = email_agent(
                st.session_state.destination,
                selected_itinerary[:500],
                st.session_state.user_name
            )
            st.session_state.export_ready = True
        st.success("✅ Document prêt !")
        st.rerun()
    
    st.markdown("### 📋 Résumé de votre voyage")
    with st.expander("📄 Voir le document complet", expanded=True):
        st.markdown(st.session_state.export_content)
    
    st.markdown("---")
    st.markdown("### 📥 Options de téléchargement")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        pdf_content = generate_pdf(
            st.session_state.export_content,
            st.session_state.destination
        )
        create_download_button(
            pdf_content,
            f"voyage_{st.session_state.destination.replace(' ', '_')}.txt",
            "📥 Télécharger (.txt)"
        )
    
    with col2:
        if st.button("📧 Envoyer par email", type="primary", use_container_width=True, key="send_email"):
            if st.session_state.user_email:
                subject, body = prepare_email_content(st.session_state.email_content)
                result = send_email_simulation(
                    st.session_state.user_email,
                    subject,
                    body
                )
                if result["success"]:
                    st.success(result["message"])
                    st.session_state.email_sent = True
            else:
                st.error("⚠️ Veuillez entrer votre email dans la sidebar")
    
    with col3:
        if st.button("🔄 Nouveau voyage", use_container_width=True, key="new_trip_step5"):
            reset_session()
            st.rerun()
    
    if st.session_state.email_sent:
        st.success("✅ Email envoyé avec succès ! Vérifiez votre boîte de réception.")
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray;">
        <p>Merci d'avoir utilisé Travel Planner AI ! ✈️</p>
        <p>LLaMA 3.1 via Groq | Multi-Agents IA | Streaming en temps réel</p>
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# 🎨 FOOTER GLOBAL
# ============================================================
st.markdown("---")
st.caption("🌍 Travel Planner AI - Projet Agent IA | Powered by Groq & LLaMA 3.1")