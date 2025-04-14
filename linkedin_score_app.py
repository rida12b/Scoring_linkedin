import streamlit as st
import json
import os
import sys
import re # Importer le module regex
from dotenv import load_dotenv
import pandas as pd
import scrape_linkedin

# Chargement des variables d'environnement
load_dotenv()

# Configuration de la page Streamlit avec thème par défaut
st.set_page_config(
    page_title="LinkedIn Profile Scorer | Évaluation professionnelle",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': """# LinkedIn Profile Scorer
        Cette application évalue les profils LinkedIn en utilisant l'IA.
        Propulsé par Proxycurl et Google Gemini."""
    }
)

# CSS personnalisé (optimisé pour thème clair)
st.markdown("""
<style>
    /* Style de base */
    * {
        font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
    }
    body {
        background-color: #f5f7fa;
    }
    .main > div {
        padding: 2rem 3rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    /* En-têtes */
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        letter-spacing: -0.01em;
        color: #1E293B;
    }
    h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
        text-align: center;
    }
    h2 {
        margin-top: 1.5rem;
        margin-bottom: 0.75rem;
        font-size: 1.75rem;
    }
    h3 {
        font-size: 1.35rem;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
        padding-left: 10px;
    }
    
    /* Style de cartes */
    .card {
        background-color: white;
        border-radius: 12px;
        padding: 1.75rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 1.75rem;
        border: 1px solid rgba(230, 230, 230, 0.7);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.12);
    }
    
    /* Style des boutons */
    div.stButton > button {
        width: 100%;
        height: 3.5rem;
        font-weight: 700;
        font-size: 1.1rem;
        border-radius: 10px;
        border: none;
        background: linear-gradient(90deg, #FF4B4B, #FF8080);
        color: white;
        text-transform: uppercase;
        letter-spacing: 2px;
        transition: all 0.3s ease;
        box-shadow: 0 6px 15px rgba(255, 75, 75, 0.3);
    }
    div.stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(255, 75, 75, 0.4);
    }
    div.stButton > button:active {
        transform: translateY(-1px);
        box-shadow: 0 5px 10px rgba(255, 75, 75, 0.2);
    }
    
    /* Style des champs de texte */
    div[data-baseweb="input"] {
        border-radius: 8px;
    }
    div[data-baseweb="input"] > div {
        background-color: white;
        border-radius: 8px;
        border: 2px solid rgba(49, 51, 63, 0.2);
        transition: all 0.2s ease;
    }
    div[data-baseweb="input"] > div:focus-within {
        box-shadow: 0 0 0 3px rgba(0, 0, 0, 0.1);
    }
    
    /* Tabs stylisés */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        border-radius: 12px;
        background: #f8fafd;
        padding: 0.35rem;
        border: 1px solid rgba(230, 230, 230, 0.7);
    }
    .stTabs [data-baseweb="tab"] {
        height: 3.2rem;
        padding: 0 1.5rem;
        border-radius: 8px;
        transition: all 0.3s ease;
        font-weight: 500;
        letter-spacing: 0.2px;
    }
    
    /* Compteur de score */
    .score-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        position: relative;
    }
    .score-circle {
        width: 180px;
        height: 180px;
        border-radius: 50%;
        background: conic-gradient(var(--score-color) var(--score-angle), #e9ecef 0);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        position: relative;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% {
            box-shadow: 0 0 0 0 rgba(var(--pulse-color), 0.7);
        }
        70% {
            box-shadow: 0 0 0 10px rgba(var(--pulse-color), 0);
        }
        100% {
            box-shadow: 0 0 0 0 rgba(var(--pulse-color), 0);
        }
    }
    .score-circle::before {
        content: "";
        position: absolute;
        width: 150px;
        height: 150px;
        background-color: white;
        border-radius: 50%;
        box-shadow: inset 0 4px 8px rgba(0, 0, 0, 0.05);
    }
    .score-value {
        font-size: 4rem;
        font-weight: 800;
        margin: 0;
        position: relative;
        z-index: 2;
        color: #1E293B;
    }
    .score-label {
        font-size: 1.1rem;
        font-weight: 600;
        margin-top: -0.75rem;
        position: relative;
        z-index: 2;
        color: #64748B;
    }
    
    /* Métriques */
    .metric-container {
        display: flex;
        flex-direction: column;
        background: linear-gradient(145deg, #ffffff, #f8fafd);
        padding: 1.25rem;
        border-radius: 12px;
        text-align: center;
        transition: all 0.3s ease;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
    }
    .metric-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
        border-color: rgba(49, 51, 63, 0.2);
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
        text-shadow: 0 1px 1px rgba(0, 0, 0, 0.05);
    }
    .metric-label {
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Styles pour les expanders */
    .stExpander > div[data-testid="stExpanderDetails"] {
         background-color: #f8fafd;
         border-radius: 12px;
         border: 1px solid #e2e8f0;
         padding: 1.25rem;
    }
    .stExpander > div[role="button"]:hover {
        background-color: rgba(151, 166, 195, 0.15);
    }
    
    /* Améliorer le rendu markdown dans l'analyse détaillée */
    .detailed-analysis-content p,
    .detailed-analysis-content ul,
    .detailed-analysis-content ol {
        font-size: 1.05rem;
        line-height: 1.8;
        margin-bottom: 1.25rem;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .card {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Justification du score avec meilleure lisibilité */
    .justification-box {
        padding: 1rem 1.25rem;
        border-radius: 6px;
        font-size: 1rem;
        line-height: 1.7;
        margin-top: 1.25rem;
    }
    
    /* Améliorations pour la section "À propos de l'outil" */
    .feature-item {
        display: flex;
        align-items: center;
        margin-bottom: 0.9rem;
        padding: 0.6rem 0.8rem;
        border-radius: 8px;
        transition: all 0.2s ease;
        background-color: #f8fafd;
    }
    .feature-item:hover {
        background-color: rgba(151, 166, 195, 0.15);
        transform: translateX(5px);
    }
    .feature-item-number {
        min-width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 12px;
        box-shadow: 0 3px 5px rgba(0, 0, 0, 0.15);
    }
    .feature-item-text {
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Appliquer un style visuel amélioré pour le thème clair
    extra_styles = """
    <style>
    /* Amélioration de la visibilité des feature-items */
    .feature-item {
        background-color: rgba(10, 77, 104, 0.1);
        border-left: 3px solid #0A4D68;
    }
    .feature-item:hover {
        background-color: rgba(10, 77, 104, 0.2);
    }
    .feature-item-number {
        background-color: #0A4D68;
        color: white;
    }
    
    /* Amélioration des cartes */
    .card {
        border-left: 3px solid #0A4D68 !important;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Amélioration des boutons */
    div.stButton > button {
        background: linear-gradient(90deg, #0A4D68, #146C94) !important;
        color: white !important;
    }
    div.stButton > button:hover {
        box-shadow: 0 10px 20px rgba(10, 77, 104, 0.4) !important;
    }
    
    /* Amélioration des sliders */
    div.stSlider > div[data-baseweb="slider"] > div > div {
        background-color: rgba(10, 77, 104, 0.6);
    }
    div.stSlider > div[data-baseweb="slider"] > div > div > div {
        background-color: #0A4D68;
        border: 2px solid white;
        box-shadow: 0 0 10px rgba(10, 77, 104, 0.5);
    }
    </style>
    """
    st.markdown(extra_styles, unsafe_allow_html=True)
    
    # Titre et description de l'application
    st.markdown("<h1>LinkedIn Profile Scorer</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; margin-bottom: 2rem;">
        <p style="font-size: 1.1rem; margin-bottom: 2rem; font-weight: 500;">
            Analysez et évaluez des profils LinkedIn selon des critères professionnels objectifs
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Carte principale
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Séparation en colonnes
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Entrée de l'URL LinkedIn dans un conteneur stylisé
        st.markdown("<h3>URL du profil LinkedIn</h3>", unsafe_allow_html=True)
        linkedin_url = st.text_input("", 
                              value="https://www.linkedin.com/in/sundarpichai/",
                              placeholder="https://www.linkedin.com/in/exemple/",
                              label_visibility="collapsed")
        
        # Bouton pour déclencher l'analyse avec style amélioré
        button_style = """
        <style>
        div.stButton > button {
            width: 100%;
            height: 3.5rem;
            font-weight: 700;
            font-size: 1.1rem;
            border-radius: 10px;
            border: none;
            background: linear-gradient(90deg, #0A4D68, #146C94);
            color: white;
            text-transform: uppercase;
            letter-spacing: 2px;
            transition: all 0.3s ease;
            box-shadow: 0 6px 15px rgba(10, 77, 104, 0.3);
        }
        div.stButton > button:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(10, 77, 104, 0.4);
        }
        div.stButton > button:active {
            transform: translateY(-1px);
            box-shadow: 0 5px 10px rgba(10, 77, 104, 0.2);
        }
        </style>
        """
        st.markdown(button_style, unsafe_allow_html=True)
        analyze_button = st.button("🔍 ANALYSER LE PROFIL", type="primary", use_container_width=True)
        
        # Paramètres de scoring
        with st.expander("⚙️ Paramètres d'évaluation"):
            st.markdown("<p style='margin-bottom: 1rem; font-weight: 500;'>Ajustez la pondération des critères d'évaluation:</p>", unsafe_allow_html=True)
            
            # Style pour les sliders
            slider_style = """
            <style>
            div.stSlider > div[data-baseweb="slider"] > div > div {
                background-color: rgba(10, 77, 104, 0.6);
            }
            div.stSlider > div[data-baseweb="slider"] > div > div > div {
                background-color: #0A4D68;
                border: 2px solid white;
                box-shadow: 0 0 10px rgba(10, 77, 104, 0.5);
            }
            </style>
            """
            st.markdown(slider_style, unsafe_allow_html=True)
            
            exp_weight = st.slider("💼 Expérience professionnelle", 0.1, 0.6, 0.4, 0.1)
            edu_weight = st.slider("🎓 Niveau d'études", 0.1, 0.6, 0.3, 0.1)
            sector_weight = st.slider("🏢 Secteur d'activité", 0.1, 0.6, 0.3, 0.1)
            
            # Niveau de détail de l'analyse
            detail_level = st.radio("📈 Niveau de détail de l'analyse:", 
                                    ["standard", "approfondi"],
                                    index=0,
                                    help="L'analyse approfondie fournit une évaluation plus complète mais prend plus de temps.")
            
            # Normaliser les poids pour qu'ils totalisent 1.0
            total = exp_weight + edu_weight + sector_weight
            exp_weight = round(exp_weight / total, 2)
            edu_weight = round(edu_weight / total, 2)
            sector_weight = round(sector_weight / total, 2)
            
            # Style pour l'info box
            info_style = """
            <style>
            div.stAlert > div {
                background-color: rgba(10, 77, 104, 0.1);
                border: 1px solid rgba(10, 77, 104, 0.5);
                border-radius: 8px;
                padding: 1rem;
            }
            </style>
            """
            st.markdown(info_style, unsafe_allow_html=True)
            st.info(f"Pondération ajustée : Expérience ({exp_weight}) · Éducation ({edu_weight}) · Secteur ({sector_weight})")
    
    with col2:
        # Informations sur l'application dans une carte stylisée
        st.markdown("<h3>À propos de l'outil</h3>", unsafe_allow_html=True)
        st.markdown("""
        <div style="margin-bottom: 1.5rem;">
            <p style="margin-bottom: 1rem; font-weight: 500;">Cette application professionnelle utilise :</p>
            <div>
                <div class="feature-item">
                    <div class="feature-item-number">
                        <span style="font-size: 0.85rem; font-weight: 600;">1</span>
                    </div>
                    <span class="feature-item-text"><strong>API Proxycurl</strong> pour l'extraction des données</span>
                </div>
                <div class="feature-item">
                    <div class="feature-item-number">
                        <span style="font-size: 0.85rem; font-weight: 600;">2</span>
                    </div>
                    <span class="feature-item-text"><strong>Google Gemini</strong> pour l'analyse approfondie</span>
                </div>
                <div class="feature-item">
                    <div class="feature-item-number">
                        <span style="font-size: 0.85rem; font-weight: 600;">3</span>
                    </div>
                    <span class="feature-item-text"><strong>Streamlit</strong> pour l'interface utilisateur</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Statut et configuration
        st.markdown("<h3>État du système</h3>", unsafe_allow_html=True)
        api_status = {
            "Proxycurl API": {"status": os.getenv("PROXYCURL_API_KEY") is not None, "text": "Active" if os.getenv("PROXYCURL_API_KEY") else "Non configurée"},
            "Gemini API": {"status": os.getenv("GEMINI_API_KEY") is not None, "text": "Active" if os.getenv("GEMINI_API_KEY") else "Non configurée"},
            "Modèle Gemini": os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
        }
        
        # Affichage du statut avec badges personnalisés
        status_style = """
        <style>
        .status-badge-active {
            display: inline-flex;
            align-items: center;
            background-color: rgba(80, 200, 120, 0.2);
            color: #50C878;
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-weight: 500;
            font-size: 0.9rem;
        }
        .status-badge-inactive {
            display: inline-flex;
            align-items: center;
            background-color: rgba(10, 77, 104, 0.2);
            color: #0A4D68;
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-weight: 500;
            font-size: 0.9rem;
        }
        .model-badge {
            display: inline-flex;
            align-items: center;
            background-color: rgba(20, 108, 148, 0.2);
            color: #146C94;
            padding: 0.4rem 0.8rem;
            border-radius: 20px;
            font-weight: 500;
            font-size: 0.9rem;
        }
        </style>
        """
        st.markdown(status_style, unsafe_allow_html=True)
        
        st.markdown(
            f"""
            <div style="margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.85rem; align-items: center;">
                    <span style="font-weight: 500;">Proxycurl API:</span>
                    <span class="status-badge-{'active' if api_status['Proxycurl API']['status'] else 'inactive'}">
                        {"✅ " + api_status["Proxycurl API"]["text"] if api_status["Proxycurl API"]["status"] else "❌ " + api_status["Proxycurl API"]["text"]}
                    </span>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.85rem; align-items: center;">
                    <span style="font-weight: 500;">Gemini API:</span>
                    <span class="status-badge-{'active' if api_status['Gemini API']['status'] else 'inactive'}">
                        {"✅ " + api_status["Gemini API"]["text"] if api_status["Gemini API"]["status"] else "❌ " + api_status["Gemini API"]["text"]}
                    </span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-weight: 500;">Modèle d'IA:</span>
                    <span class="model-badge">
                        {api_status["Modèle Gemini"]}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Section de résultats
    if analyze_button and linkedin_url:
        if not linkedin_url or 'linkedin.com/in/' not in linkedin_url:
            st.error("⚠️ Veuillez entrer une URL LinkedIn valide (ex: https://www.linkedin.com/in/nom-utilisateur/).")
        else:
            with st.spinner('🔄 Analyse en cours... Veuillez patienter.'):
                try:
                    # Appel au script d'analyse avec les paramètres de pondération
                    st.session_state["result"] = scrape_linkedin.process_linkedin_profile(
                        linkedin_url, 
                        exp_weight=exp_weight,
                        edu_weight=edu_weight,
                        sector_weight=sector_weight,
                        detail_level=detail_level
                    )
                    show_results()
                except Exception as e:
                    st.error(f"❌ Une erreur s'est produite lors de l'analyse: {str(e)}")
    elif "result" in st.session_state:
         # Afficher les résultats précédents si disponibles
         show_results()

def show_results():
    """Affiche les résultats de l'analyse"""
    if "result" not in st.session_state:
        return
    
    result = st.session_state["result"]
    
    # Style pour les résultats
    score_style = """
    <style>
    /* Style pour les onglets */
    .stTabs [data-baseweb="tab-list"] {
        background-color: rgba(10, 77, 104, 0.05);
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(10, 77, 104, 0.2);
        color: #0A4D68;
    }
    
    /* Style pour le cercle de score */
    .score-circle {
        background: conic-gradient(#0A4D68 var(--score-angle), rgba(31, 41, 55, 0.4) 0) !important;
    }
    @keyframes glow {
        0% { box-shadow: 0 0 10px rgba(10, 77, 104, 0.5); }
        50% { box-shadow: 0 0 20px rgba(10, 77, 104, 0.8); }
        100% { box-shadow: 0 0 10px rgba(10, 77, 104, 0.5); }
    }
    .score-circle {
        animation: glow 3s infinite !important;
    }
    
    /* Style pour les métriques */
    .metric-container {
        border-left: 3px solid #0A4D68 !important;
    }
    </style>
    """
    st.markdown(score_style, unsafe_allow_html=True)
    
    # Séparation en tabs pour organiser les résultats
    tab1, tab2, tab3 = st.tabs(["📋 Synthèse", "🔍 Analyse détaillée", "🧩 Données techniques"])
    
    with tab1:
        # Carte principale de résultat
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        # Titre de section
        st.markdown("<h2 style='text-align: center; margin-bottom: 1.5rem;'>Résultats de l'évaluation</h2>", unsafe_allow_html=True)
        
        # Affichage du résumé avec une mise en forme visuelle
        score = result.get("score", 0)
        
        # Lignes principales
        col_profile, col_score = st.columns([2, 1], gap="large")
        
        with col_profile:
            # Informations sur le profil dans un cadre élégant - Amélioration du contraste
            st.markdown(f"""
            <div style="background: linear-gradient(to right, rgba(10, 77, 104, 0.05), rgba(255, 255, 255, 0.01)); border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); border-left: 3px solid #0A4D68; margin-bottom: 1.5rem;">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <h3 style="margin: 0; font-size: 1.8rem; color: #1E293B;">{result['details'].get('nom', 'Non spécifié')}</h3>
                </div>
                <p style="font-size: 1.15rem; margin-bottom: 1.5rem; font-weight: 500; padding-left: 20px; color: #475569;">{result['details'].get('titre', 'Non spécifié')}</p>
            </div>
            
            <h4 style="margin-bottom: 1.2rem; font-size: 1.25rem; color: #0A4D68; border-left: 3px solid #0A4D68; padding-left: 10px;">Critères d'évaluation</h4>
            """, unsafe_allow_html=True)
            
            # Affichage des métriques en grille améliorée
            cols = st.columns(3)
            with cols[0]:
                st.markdown(f"""
                <div class="metric-container" style="position: relative; overflow: hidden;">
                    <div class="metric-value" style="color: #0A4D68;">{result['details'].get('experience_annees', 'N/A')}</div>
                    <div class="metric-label">Années d'expérience</div>
                </div>
                """, unsafe_allow_html=True)
                
            with cols[1]:
                st.markdown(f"""
                <div class="metric-container" style="position: relative; overflow: hidden;">
                    <div class="metric-value" style="color: #0A4D68;">{result['details'].get('niveau_education', 'N/A')}</div>
                    <div class="metric-label">Niveau d'éducation</div>
                </div>
                """, unsafe_allow_html=True)
                
            with cols[2]:
                st.markdown(f"""
                <div class="metric-container" style="position: relative; overflow: hidden;">
                    <div class="metric-value" style="color: #0A4D68;">{result['details'].get('secteur_activite', 'N/A')}</div>
                    <div class="metric-label">Secteur d'activité</div>
                </div>
                """, unsafe_allow_html=True)
            
        with col_score:
            # Déterminer les couleurs en fonction du score
            label = ""
            
            if score >= 8:
                label = "Excellent"
            elif score >= 6:
                label = "Bon"
            elif score >= 4:
                label = "Moyen"
            else:
                label = "Faible"
                
            # Calcul de l'angle pour le gradient conique
            angle = score * 36  # 360 degrés / 10 = 36 degrés par point
            
            # Visualisation du score avec une jauge personnalisée - Amélioration du contraste
            st.markdown(f"""
            <div style="background: rgba(243, 244, 246, 0.7); border-radius: 12px; padding: 1.5rem; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); height: 100%; border-left: 3px solid #0A4D68;">
                <h3 style="margin-bottom: 1rem; text-align: center; font-size: 1.25rem; color: #1E293B;">Score global</h3>
                <div class="score-container">
                    <div class="score-circle" style="--score-angle: {angle}deg;">
                        <div style="display: flex; flex-direction: column; align-items: center;">
                            <p class="score-value" style="color: #0A4D68;">{score}</p>
                            <p class="score-label" style="color: #475569;">/10</p>
                        </div>
                    </div>
                    <div style="background-color: #0A4D68; color: white; padding: 0.4rem 1rem; border-radius: 20px; font-weight: 600; margin-top: 0.5rem;">
                        {label}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        # Justification dans une section dédiée et visuellement améliorée - Amélioration du contraste
        st.markdown(f"""
        <div style="margin-top: 2rem; position: relative;">
            <h4 style="margin-bottom: 1rem; font-size: 1.25rem; color: #0A4D68; border-left: 3px solid #0A4D68; padding-left: 10px;">Justification</h4>
            <div class="justification-box" style="background: linear-gradient(to right, rgba(10, 77, 104, 0.05), rgba(255, 255, 255, 0.01)); border-radius: 12px; padding: 1.5rem; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1); border-left: 3px solid #0A4D68;">
                <div style="display: flex; align-items: flex-start;">
                    <div style="margin-right: 15px; background-color: #0A4D68; color: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-top: 3px;">
                        <span style="font-weight: bold; font-size: 0.8rem;">i</span>
                    </div>
                    <div style="font-size: 1.05rem; line-height: 1.7; color: #1E293B;">
                        {result.get('justification', 'Aucune justification fournie')}
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Ajouter une section récapitulative avec la pondération utilisée - Amélioration du contraste
        st.markdown(f"""
        <div style="margin-top: 2rem; background-color: rgba(10, 77, 104, 0.05); border-radius: 12px; padding: 1rem 1.5rem; border: 1px solid rgba(10, 77, 104, 0.2); border-left: 3px solid #0A4D68;">
            <h4 style="margin-bottom: 0.75rem; font-size: 1.1rem; color: #0A4D68;">📊 Pondération utilisée</h4>
            <div style="display: flex; justify-content: space-around; text-align: center;">
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div style="font-weight: 600; font-size: 1.2rem; color: #0A4D68;">
                        {result.get('ponderations', {}).get('experience', '40')}%
                    </div>
                    <div style="font-size: 0.9rem; color: #475569;">Expérience</div>
                </div>
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div style="font-weight: 600; font-size: 1.2rem; color: #0A4D68;">
                        {result.get('ponderations', {}).get('education', '30')}%
                    </div>
                    <div style="font-size: 0.9rem; color: #475569;">Éducation</div>
                </div>
                <div style="display: flex; flex-direction: column; align-items: center;">
                    <div style="font-weight: 600; font-size: 1.2rem; color: #0A4D68;">
                        {result.get('ponderations', {}).get('secteur', '30')}%
                    </div>
                    <div style="font-size: 0.9rem; color: #475569;">Secteur</div>
                </div>
            </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        # Affichage des détails de l'analyse
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color: #0A4D68; border-left: 3px solid #0A4D68; padding-left: 10px;'>Raisonnement détaillé de l'IA</h3>", unsafe_allow_html=True)
        
        if "raisonnement" in result and result["raisonnement"]:
            # Nettoyer le texte brut
            raisonnement_text = result["raisonnement"]
            # Supprimer les délimiteurs de blocs de code JSON/Markdown
            cleaned_raisonnement = re.sub(r"^```(?:json)?\n?|'''\n?$", '', raisonnement_text, flags=re.MULTILINE).strip()
            
            # Structure du raisonnement en sections
            st.markdown("""
            <style>
            .detail-section {
                background-color: rgba(10, 77, 104, 0.05);
                border-radius: 8px;
                padding: 1.25rem;
                margin-bottom: 1.5rem;
                border-left: 3px solid #0A4D68;
            }
            .detail-section h4 {
                color: #0A4D68;
                margin-bottom: 1rem;
                font-size: 1.2rem;
                display: flex;
                align-items: center;
            }
            .detail-section p {
                margin-bottom: 0.75rem;
                line-height: 1.7;
                color: #1E293B;
            }
            .detail-section-icon {
                background-color: #0A4D68;
                color: white;
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 12px;
                font-size: 16px;
            }
            .score-detail {
                display: flex;
                align-items: center;
                margin-top: 1rem;
                padding: 0.75rem;
                background-color: rgba(10, 77, 104, 0.1);
                border-radius: 6px;
            }
            .score-detail-number {
                font-size: 1.5rem;
                font-weight: 700;
                color: #0A4D68;
                margin-right: 1rem;
                min-width: 50px;
                text-align: center;
            }
            .score-detail-text {
                flex-grow: 1;
            }
            .score-calculation {
                background-color: #f8fafc;
                border: 1px dashed #cbd5e1;
                border-radius: 6px;
                padding: 1rem;
                margin: 1rem 0;
                font-family: monospace;
                line-height: 1.6;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Section score global
            st.markdown(f"""
            <div class="detail-section">
                <h4>
                    <div class="detail-section-icon">🏆</div>
                    Score global et calcul
                </h4>
                <p>Score final : <strong style="font-size: 1.2rem; color: #0A4D68;">{result.get('score', 0)}/10</strong></p>
                <div class="score-calculation">
                    <strong>Méthode de calcul :</strong><br>
                    - Expérience ({result.get('ponderations', {}).get('experience', 40)}%) : {result["details"].get("experience_annees", "N/A")} années<br>
                    - Éducation ({result.get('ponderations', {}).get('education', 30)}%) : {result["details"].get("niveau_education", "N/A")}<br>
                    - Secteur ({result.get('ponderations', {}).get('secteur', 30)}%) : {result["details"].get("secteur_activite", "N/A")}
                </div>
                <p>{result.get('justification', '').split('\n\n')[0]}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Créer un résumé court pour chaque section
            # Section expérience professionnelle
            st.markdown("""
            <div class="detail-section">
                <h4>
                    <div class="detail-section-icon">💼</div>
                    Analyse de l'expérience professionnelle
                </h4>
            """, unsafe_allow_html=True)
            
            # Créer un paragraphe court pour l'expérience
            experience_text = f"Le candidat possède {result['details'].get('experience_annees', 'N/A')} années d'expérience professionnelle. "
            if "justification" in result:
                # Extraire des phrases pertinentes sur l'expérience
                justification = result.get('justification', '')
                exp_keywords = ["expérience", "carrière", "travaillé", "poste", "emploi", "fonction", "années"]
                sentences = re.split(r'(?<=[.!?])\s+', justification)
                for sentence in sentences:
                    if any(keyword in sentence.lower() for keyword in exp_keywords) and "éducation" not in sentence.lower() and "secteur" not in sentence.lower() and len(sentence) < 200:
                        experience_text += sentence + " "
                        break
            
            st.markdown(f"""
                <p>{experience_text}</p>
                <div class="score-detail">
                    <div class="score-detail-number">{result["details"].get("experience_annees", "N/A")}</div>
                    <div class="score-detail-text">années d'expérience professionnelle identifiées</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Section éducation
            st.markdown("""
            <div class="detail-section">
                <h4>
                    <div class="detail-section-icon">🎓</div>
                    Analyse du parcours éducatif
                </h4>
            """, unsafe_allow_html=True)
            
            # Créer un paragraphe court pour l'éducation
            education_text = f"Le niveau d'éducation identifié est '{result['details'].get('niveau_education', 'N/A')}'. "
            if "justification" in result:
                # Extraire des phrases pertinentes sur l'éducation
                justification = result.get('justification', '')
                edu_keywords = ["éducation", "formation", "diplôme", "master", "études", "école", "université", "niveau"]
                sentences = re.split(r'(?<=[.!?])\s+', justification)
                for sentence in sentences:
                    if any(keyword in sentence.lower() for keyword in edu_keywords) and "expérience" not in sentence.lower() and "secteur" not in sentence.lower() and len(sentence) < 200:
                        education_text += sentence + " "
                        break
            
            st.markdown(f"""
                <p>{education_text}</p>
                <div class="score-detail">
                    <div class="score-detail-number">{result["details"].get("niveau_education", "N/A")}</div>
                    <div class="score-detail-text">niveau d'éducation identifié</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Section secteur d'activité
            st.markdown("""
            <div class="detail-section">
                <h4>
                    <div class="detail-section-icon">🏢</div>
                    Analyse du secteur d'activité
                </h4>
            """, unsafe_allow_html=True)
            
            # Créer un paragraphe court pour le secteur
            sector_text = f"Le secteur d'activité identifié est '{result['details'].get('secteur_activite', 'N/A')}'. "
            if "justification" in result:
                # Extraire des phrases pertinentes sur le secteur
                justification = result.get('justification', '')
                sector_keywords = ["secteur", "activité", "industrie", "domaine", "technologie", "marché"]
                sentences = re.split(r'(?<=[.!?])\s+', justification)
                for sentence in sentences:
                    if any(keyword in sentence.lower() for keyword in sector_keywords) and "expérience" not in sentence.lower() and "éducation" not in sentence.lower() and len(sentence) < 200:
                        sector_text += sentence + " "
                        break
            
            st.markdown(f"""
                <p>{sector_text}</p>
                <div class="score-detail">
                    <div class="score-detail-number">{result["details"].get("secteur_activite", "N/A")}</div>
                    <div class="score-detail-text">secteur d'activité identifié</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Raisonnement complet (caché dans un expander)
            with st.expander("Voir le raisonnement complet de l'IA"):
                st.markdown(f'<div class="detailed-analysis-content" style="color: #1E293B; white-space: pre-line;">{cleaned_raisonnement}</div>', unsafe_allow_html=True)
                
        else:
            st.markdown('<div style="background-color: rgba(10, 77, 104, 0.05); padding: 1rem; border-radius: 8px; border-left: 3px solid #0A4D68;">', unsafe_allow_html=True)
            st.info("ℹ️ Aucun détail d'analyse fourni par l'IA pour ce profil.")
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    with tab3:
        # Affichage des données brutes
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color: #0A4D68; border-left: 3px solid #0A4D68; padding-left: 10px;'>Données techniques</h3>", unsafe_allow_html=True)
        
        # Style pour les boutons de téléchargement
        download_button_style = """
        <style>
        div.stDownloadButton > button {
            background-color: rgba(10, 77, 104, 0.1) !important;
            color: #0A4D68 !important;
            border: 1px solid rgba(10, 77, 104, 0.3) !important;
            padding: 0.5rem 1rem !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            transition: all 0.3s !important;
        }
        div.stDownloadButton > button:hover {
            background-color: rgba(10, 77, 104, 0.2) !important;
            box-shadow: 0 4px 8px rgba(10, 77, 104, 0.2) !important;
        }
        </style>
        """
        st.markdown(download_button_style, unsafe_allow_html=True)
        
        # Tabs internes pour différents formats de téléchargement
        download_tabs = st.tabs(["📄 Format JSON", "📊 Format CSV"])
        
        with download_tabs[0]:
            st.json(result)
            
            # Option pour télécharger les résultats
            json_str = json.dumps(result, indent=2, ensure_ascii=False)
            st.download_button(
                label="💾 Télécharger (JSON)",
                data=json_str,
                file_name="linkedin_profile_analysis.json",
                mime="application/json"
            )
        
        with download_tabs[1]:
            # Option pour télécharger en CSV
            csv_data = {
                "URL": [result.get("url", "")],
                "Nom": [result["details"].get("nom", "")],
                "Titre": [result["details"].get("titre", "")],
                "Score": [result.get("score", 0)],
                "Expérience (années)": [result["details"].get("experience_annees", "")],
                "Niveau d'éducation": [result["details"].get("niveau_education", "")],
                "Secteur d'activité": [result["details"].get("secteur_activite", "")]
            }
            csv_df = pd.DataFrame(csv_data)
            
            # Affichage du tableau
            st.dataframe(csv_df)
            
            # Bouton de téléchargement
            csv = csv_df.to_csv(index=False)
            st.download_button(
                label="💾 Télécharger (CSV)",
                data=csv,
                file_name="linkedin_profile_analysis.csv",
                mime="text/csv"
            )
            
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main() 