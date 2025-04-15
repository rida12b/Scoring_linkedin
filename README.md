# LinkedIn Profile Scorer - Application Streamlit

## 📋 Description

LinkedIn Profile Scorer est un outil d'analyse qui :
- Extrait les données de profils LinkedIn publics via l'API Proxycurl
- Analyse intelligemment ces données avec Google Gemini AI
- Génère un score global basé sur l'expérience, l'éducation et le secteur d'activité
- Présente les résultats détaillés dans une interface Streamlit claire et intuitive

## ✨ Fonctionnalités

- **Extraction de données LinkedIn** via l'API Proxycurl (sans risque de blocage de compte)
- **Analyse intelligente** alimentée par Google Gemini AI
- **Système de scoring personnalisable** basé sur trois critères principaux :
  - Expérience professionnelle (pondération ajustable)
  - Niveau d'éducation (pondération ajustable)
  - Secteur d'activité (pondération ajustable)
- **Interface utilisateur moderne** développée avec Streamlit
- **Analyse détaillée** avec explication du raisonnement pour chaque critère
- **Gestion robuste des erreurs** pour traiter les cas de données manquantes ou incomplètes

## 🔧 Prérequis

Pour utiliser cette application, vous aurez besoin :
- Python 3.8 ou supérieur
- Une clé API Proxycurl (pour l'extraction des données LinkedIn)
- Une clé API Google Gemini (pour l'analyse des profils)
- Pip (gestionnaire de paquets Python)

## 🚀 Installation

1. Clonez ce dépôt :
```bash
git clone https://github.com/rida12b/Scoring_linkedin.git
cd usecase_ayomi_scoring
```

2. Créez un environnement virtuel et activez-le :
```bash
python -m venv venv
# Sur Windows
venv\Scripts\activate
# Sur macOS/Linux
source venv/bin/activate
```

3. Installez les dépendances :
```bash
pip install -r requirements.txt
```

4. Créez un fichier `.env` à la racine du projet avec vos clés API :
```
PROXYCURL_API_KEY=votre_clé_proxycurl
GEMINI_API_KEY=votre_clé_gemini
```

## 💻 Utilisation

1. Lancez l'application Streamlit :
```bash
streamlit run linkedin_score_app.py
```

2. Accédez à l'interface via votre navigateur (généralement http://localhost:8501)

3. Entrez l'URL du profil LinkedIn à analyser

4. Ajustez les pondérations si nécessaire

5. Cliquez sur "Analyser le profil" et attendez les résultats

## 🏗️ Structure du Projet

```
/
├── linkedin_score_app.py   # Application Streamlit principale
├── scrape_linkedin.py      # Script de scraping et scoring LinkedIn
├── .streamlit/             # Configuration Streamlit
│   └── config.toml         # Paramètres de thème et configuration
├── .env                    # Variables d'environnement (clés API)
├── requirements.txt        # Dépendances du projet
├── README.md               # Documentation
└── suivi_projet.md         # Journal de développement
```

## 🐛 Gestion des Erreurs

L'application utilise une approche robuste pour la gestion des erreurs :

1. **Extraction des données :** Si l'API Proxycurl échoue, le système procédera tout de même avec une analyse dégradée.

2. **Analyse IA :** En cas d'échec de l'analyse par Gemini, le système utilise des méthodes de calcul de secours pour générer un score basé sur les données brutes.

3. **Données manquantes :** Le système détecte et gère les cas où l'expérience, l'éducation ou le secteur sont manquants.

4. **Interface utilisateur :** Les erreurs sont présentées de manière claire à l'utilisateur avec des suggestions pour résoudre le problème.

## 🎨 Personnalisation

L'application permet plusieurs niveaux de personnalisation :

1. **Pondérations :** Ajustez l'importance relative de l'expérience, l'éducation et le secteur.

2. **Thème :** L'interface utilise le thème Streamlit configuré dans `.streamlit/config.toml`.

3. **Prompt IA :** La personnalisation du prompt est possible pour les utilisateurs avancés en modifiant `scrape_linkedin.py`.

## 🔒 Limites Connues

- L'analyse est limitée aux profils LinkedIn publics.
- La qualité de l'analyse dépend de la complétude du profil LinkedIn.
- Les quotas API de Proxycurl et Gemini peuvent limiter le nombre d'analyses.
- L'analyse est basée sur un nombre limité de critères et pourrait ne pas refléter toutes les nuances d'un profil professionnel.

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.

## 📞 Contact

Pour toute question ou suggestion, n'hésitez pas à me contacter à travers les issues GitHub ou par email à [rida.boualam@outlook.fr]. 