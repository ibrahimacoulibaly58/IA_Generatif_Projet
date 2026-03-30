import streamlit as st
from datetime import datetime

# ============================================================
# 📄 GÉNÉRATION PDF
# ============================================================
def generate_pdf(content, destination):
    """
    Génère un fichier PDF à partir du contenu formaté.
    Utilise une approche simple avec streamlit (sans librairie externe lourde).
    
    Note: Pour un vrai PDF, on utiliserait fpdf ou reportlab.
    Ici on crée un fichier texte formaté qui peut être téléchargé.
    """
    # En-tête du document
    pdf_content = f"""
═══════════════════════════════════════════════════════════════
                    ✈️ PLAN DE VOYAGE
═══════════════════════════════════════════════════════════════

🌍 Destination : {destination}
📅 Généré le : {datetime.now().strftime('%d/%m/%Y à %H:%M')}

═══════════════════════════════════════════════════════════════

{content}

═══════════════════════════════════════════════════════════════
                    📞 CONTACT & SUPPORT
═══════════════════════════════════════════════════════════════

Pour toute modification ou question, contactez-nous à :
📧 support@travelplanner-ai.com

Merci d'avoir utilisé Travel Planner AI ! ✨

═══════════════════════════════════════════════════════════════
"""
    return pdf_content


def create_download_button(content, filename, label="📥 Télécharger en PDF"):
    """
    Crée un bouton de téléchargement Streamlit.
    """
    st.download_button(
        label=label,
        data=content,
        file_name=filename,
        mime="text/plain"  # Pour un vrai PDF, utiliser "application/pdf"
    )


# ============================================================
# 📧 SIMULATION ENVOI EMAIL
# ============================================================
def send_email_simulation(user_email, subject, body):
    """
    Simule l'envoi d'un email (pour la démo).
    
    Dans un projet réel, on utiliserait smtplib ou une API comme SendGrid.
    """
    # Simulation réussie
    return {
        "success": True,
        "message": f"✅ Email envoyé avec succès à {user_email}",
        "subject": subject,
        "timestamp": datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    }


def prepare_email_content(email_response):
    """
    Extrait l'objet et le corps de l'email généré par l'IA.
    """
    lines = email_response.split('\n')
    subject = ""
    body = ""
    in_body = False
    
    for line in lines:
        if line.startswith("Objet :") or line.startswith("Subject:"):
            subject = line.split(":", 1)[1].strip()
            in_body = True
        elif in_body:
            body += line + "\n"
    
    return subject.strip(), body.strip()


# ============================================================
# 🎯 GESTION DES ÉTATS (SESSION STATE)
# ============================================================
def init_session_state():
    """
    Initialise tous les états de session nécessaires.
    """
    defaults = {
        "step": 1,                    # Étape actuelle du workflow (1-5)
        "destination": "",            # Destination choisie
        "start_date": None,           # Date de début
        "end_date": None,             # Date de fin
        "interests": "",              # Centres d'intérêt
        "origin": "France",           # Lieu de départ
        "budget": "moyen",            # Budget hébergement
        "user_name": "",              # Nom de l'utilisateur
        "user_email": "",             # Email de l'utilisateur
        
        "profile_generated": False,   # Profil généré
        "itinerary_option_a": None,   # Itinéraire option A
        "itinerary_option_b": None,   # Itinéraire option B
        "selected_option": None,      # Option choisie (A ou B)
        "comparison": None,           # Comparaison des options
        
        "transport_generated": False, # Transport généré
        "transport_content": None,    # Contenu transport
        
        "hotel_generated": False,     # Hôtel généré
        "hotel_content": None,        # Contenu hôtel
        
        "export_ready": False,        # Export prêt
        "export_content": None,       # Contenu export
        "email_sent": False,          # Email envoyé
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_session():
    """
    Réinitialise toute la session pour un nouveau voyage.
    """
    for key in st.session_state.keys():
        del st.session_state[key]
    init_session_state()


def next_step():
    """Passe à l'étape suivante"""
    st.session_state.step = min(st.session_state.step + 1, 5)


def prev_step():
    """Retourne à l'étape précédente"""
    st.session_state.step = max(st.session_state.step - 1, 1)


# ============================================================
# 🎨 MISE EN FORME
# ============================================================
def display_step_indicator(current_step):
    """
    Affiche une barre de progression des étapes.
    """
    steps = [
        "📋 Infos",
        "🗺️ Itinéraire",
        "🚄 Transport",
        "🏨 Hôtel",
        "📤 Export"
    ]
    
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            if i + 1 == current_step:
                st.markdown(f"**{steps[i]}**")
            elif i + 1 < current_step:
                st.markdown(f"✅ {steps[i]}")
            else:
                st.markdown(f"⏳ {steps[i]}")
    
    st.progress(current_step / 5)


def display_agent_thinking(agent_name):
    """
    Affiche un message pendant que l'agent réfléchit.
    """
    with st.spinner(f"🤖 {agent_name} réfléchit..."):
        pass  # Le spinner gère l'affichage