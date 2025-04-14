import requests
import json
import sys
import google.generativeai as genai
import re
import os
from dotenv import load_dotenv

# Chargement des variables d'environnement
load_dotenv()

# Configuration Proxycurl
API_KEY = os.getenv("PROXYCURL_API_KEY")
API_ENDPOINT = "https://nubela.co/proxycurl/api/v2/linkedin"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# Configuration Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
genai.configure(api_key=GEMINI_API_KEY)

def extract_linkedin_data(linkedin_url):
    """
    Extrait les données d'un profil LinkedIn via l'API Proxycurl
    """
    print(f"Extraction des données du profil: {linkedin_url}")
    
    params = {
        "url": linkedin_url,
        "fallback_to_cache": "on-error",
        "use_cache": "if-present"
    }
    
    try:
        response = requests.get(API_ENDPOINT, params=params, headers=HEADERS)
        
        # Affichage des détails de la requête et de la réponse pour le debugging
        print("\n===== DÉTAILS DE LA REQUÊTE =====")
        print(f"URL: {response.request.url}")
        print(f"Headers: {dict(response.request.headers)}")  # Masque l'API key
        
        print("\n===== DÉTAILS DE LA RÉPONSE =====")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Tenter de parser le JSON pour vérifier sa validité
        try:
            data = response.json()
            print("\n===== CONTENU DE LA RÉPONSE (JSON) =====")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        except json.JSONDecodeError:
            print("\n===== CONTENU DE LA RÉPONSE (RAW) =====")
            print(response.text[:2000])  # Afficher les 2000 premiers caractères pour éviter une sortie trop longue
            print("..." if len(response.text) > 2000 else "")
            print("\n[ERREUR] La réponse n'est pas au format JSON valide")
            return None
        
    except requests.exceptions.HTTPError as http_err:
        print(f"Erreur HTTP: {http_err}")
        return None
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Erreur de connexion: {conn_err}")
        return None
    except requests.exceptions.Timeout as timeout_err:
        print(f"Erreur de timeout: {timeout_err}")
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Erreur de requête: {req_err}")
        return None
    except Exception as e:
        print(f"Erreur inconnue: {e}")
        return None

def analyze_with_gemini(profile_data, exp_weight=0.4, edu_weight=0.3, sector_weight=0.3, detail_level="standard"):
    """
    Utilise Gemini Flash Thinking pour analyser le profil et générer un score
    basé sur l'expérience, l'éducation et le secteur d'activité avec les pondérations spécifiées
    
    Args:
        profile_data (dict): Données du profil LinkedIn
        exp_weight (float): Poids pour l'expérience professionnelle (0-1)
        edu_weight (float): Poids pour le niveau d'éducation (0-1)
        sector_weight (float): Poids pour le secteur d'activité (0-1)
        detail_level (str): Niveau de détail de l'analyse ("standard" ou "approfondi")
    """
    if not profile_data:
        return {
            "error": "Données de profil insuffisantes pour l'analyse",
            "score": 0,
            "details": {
                "experience_annees": 0,
                "niveau_education": "Inconnu",
                "secteur_activite": "Inconnu"
            }
        }
    
    # Configuration du modèle Gemini
    generation_config = {
        "temperature": 0.2 if detail_level == "standard" else 0.3,
        "top_p": 0.95,
        "top_k": 0,
        "max_output_tokens": 2048 if detail_level == "standard" else 4096,
    }
    
    # Utilisation du modèle Gemini 2.0 Flash Thinking
    model = genai.GenerativeModel(
        model_name=GEMINI_MODEL,
        generation_config=generation_config
    )
    
    # Construction du prompt pour le LLM avec demande explicite de score facilement extractible
    detail_instructions = """
    Pour l'analyse standard:
    - Calcule le nombre total d'années d'expérience (même si les dates sont incomplètes, estime au mieux)
    - Détermine le niveau d'éducation (Doctorat, Master, Licence, BTS/DUT, Baccalauréat, Aucun)
    - Identifie le secteur d'activité (Technologie, Finance, Santé, Production, Commerce, Éducation, Autre)
    """
    
    if detail_level == "approfondi":
        detail_instructions = """
        Pour cette analyse approfondie:
        
        1. EXPÉRIENCE PROFESSIONNELLE:
           - Calcule le nombre total d'années d'expérience avec précision
           - Évalue la progression de carrière et les promotions
           - Analyse la pertinence des postes occupés dans le secteur
           - Évalue la diversité des compétences acquises
           - Identifie les périodes d'inactivité et leur justification
           - Note la présence d'expérience internationale ou multiculturelle
        
        2. ÉDUCATION:
           - Détermine précisément le niveau d'éducation (Doctorat, Master, Licence, BTS/DUT, Baccalauréat, Aucun)
           - Évalue la qualité et la réputation des établissements fréquentés
           - Analyse la pertinence des formations par rapport au parcours professionnel
           - Identifie les certifications professionnelles pertinentes
           - Évalue la formation continue et l'apprentissage permanent
        
        3. SECTEUR D'ACTIVITÉ:
           - Identifie le secteur principal et les sous-secteurs d'activité
           - Évalue l'expertise sectorielle et la spécialisation
           - Analyse la pertinence du secteur dans le marché actuel
           - Identifie les tendances et évolutions du secteur concerné
           - Évalue la transférabilité des compétences vers d'autres secteurs
           
        4. FACTEURS SUPPLÉMENTAIRES (à inclure dans l'analyse narrative):
           - Compétences techniques et soft skills identifiables
           - Leadership et gestion d'équipe
           - Réalisations quantifiables et impact mesurable
           - Présence internationale et expérience multiculturelle
           - Activités annexes (bénévolat, mentorat, publications)
        """
        
    prompt = f"""
    Analyse le profil LinkedIn suivant et génère un score de 0 à 10 basé sur:
    1. Les années d'expérience professionnelle ({int(exp_weight*100)}% du score)
    2. Le niveau d'éducation ({int(edu_weight*100)}% du score)
    3. Le secteur d'activité ({int(sector_weight*100)}% du score)
    
    Voici le profil à analyser (au format JSON):
    {json.dumps(profile_data, indent=2, ensure_ascii=False)}
    
    {detail_instructions}
    
    IMPORTANT: Dans ta réponse, toujours inclure une ligne clairement identifiable "Score final: X.XX/10" 
    pour faciliter l'extraction du score, même si le reste du JSON est mal formaté.
    
    Montre ton raisonnement étape par étape puis réponds avec un JSON contenant:
    1. Un score global (0-10) avec deux décimales
    2. Une justification détaillée du score
    3. Les détails de l'analyse (années d'expérience estimées, niveau d'éducation identifié, secteur d'activité déterminé)
    
    Le JSON doit suivre exactement ce format (en remplaçant les exemples par tes vraies valeurs):
    {{
        "score": 7.25,
        "justification": "Explication du score...",
        "details": {{
            "experience_annees": 8,
            "niveau_education": "Master",
            "secteur_activite": "Technologie"
        }}
    }}
    """
    
    try:
        # Appel à l'API Gemini pour l'analyse
        response = model.generate_content(prompt)
        
        # Extraction de la réponse
        gemini_response = response.text
        
        # Amélioration de l'extraction JSON - recherche de plusieurs façons
        
        # 1. Tentative d'extraction directe du JSON entier
        json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
        json_matches = re.findall(json_pattern, gemini_response, re.DOTALL)
        
        for json_str in json_matches:
            try:
                result = json.loads(json_str)
                if "score" in result:
                    # JSON valide avec score trouvé
                    result["raisonnement"] = gemini_response
                    return result
            except json.JSONDecodeError:
                continue
        
        # 2. Recherche de JSON sans backticks
        json_start = gemini_response.find('{')
        json_end = gemini_response.rfind('}') + 1
        
        if json_start >= 0 and json_end > json_start:
            json_str = gemini_response[json_start:json_end]
            try:
                # Tentative de parsing du JSON
                result = json.loads(json_str)
                
                # Ajout du raisonnement complet pour référence
                result["raisonnement"] = gemini_response
                
                return result
            except json.JSONDecodeError:
                pass  # Continue vers la méthode suivante

        # 3. Extraction directe des valeurs clés si le JSON n'est pas valide
        score_pattern = r'Score final:\s*(\d+[\.,]\d+)\/10'
        score_match = re.search(score_pattern, gemini_response)
        
        exp_pattern = r'(?:années|annees|expérience|experience)[^\d]*(\d+)'
        exp_match = re.search(exp_pattern, gemini_response, re.IGNORECASE)
        
        edu_pattern = r'(?:niveau|education)[^:]*:\s*["\']*([^"\',.]+)'
        edu_match = re.search(edu_pattern, gemini_response, re.IGNORECASE)
        
        sector_pattern = r'(?:secteur|activite|activité)[^:]*:\s*["\']*([^"\',.]+)'
        sector_match = re.search(sector_pattern, gemini_response, re.IGNORECASE)
        
        if score_match:
            score = float(score_match.group(1).replace(',', '.'))
            
            # Création d'un résultat structuré à partir des extractions partielles
            return {
                "score": score,
                "justification": "Score extrait directement du texte de l'analyse.",
                "details": {
                    "experience_annees": exp_match.group(1) if exp_match else "Non déterminé",
                    "niveau_education": edu_match.group(1) if edu_match else "Non déterminé",
                    "secteur_activite": sector_match.group(1) if sector_match else "Non déterminé"
                },
                "raisonnement": gemini_response
            }
            
        # Si aucun JSON ou score n'a pu être extrait
        return {
            "error": "Impossible d'extraire un score ou un JSON valide de la réponse.",
            "raw_response": gemini_response
        }

    except Exception as e:
        print(f"Erreur lors de l'analyse avec Gemini: {e}")
        return {
            "error": f"Erreur lors de l'analyse avec Gemini: {str(e)}",
            "score": 0
        }

def process_linkedin_profile(linkedin_url, exp_weight=0.4, edu_weight=0.3, sector_weight=0.3, detail_level="standard"):
    """
    Traite un profil LinkedIn complet et retourne les résultats formatés
    pour l'interface utilisateur
    
    Cette fonction est utilisée par l'interface Streamlit
    
    Args:
        linkedin_url (str): URL du profil LinkedIn à analyser
        exp_weight (float): Poids pour l'expérience professionnelle (0-1)
        edu_weight (float): Poids pour le niveau d'éducation (0-1)
        sector_weight (float): Poids pour le secteur d'activité (0-1)
        detail_level (str): Niveau de détail de l'analyse ("standard" ou "approfondi")
    
    Returns:
        dict: Résultats formatés de l'analyse
    """
    # Extraction des données via Proxycurl
    profile_data = extract_linkedin_data(linkedin_url)
    
    if not profile_data:
        raise Exception("Impossible d'extraire les données du profil LinkedIn")
    
    # Analyse avec Gemini
    results = analyze_with_gemini(profile_data, exp_weight, edu_weight, sector_weight, detail_level)
    
    # Préparation des résultats pour l'affichage
    if "error" in results:
        error_message = results["error"]
        raise Exception(f"Erreur lors de l'analyse: {error_message}")
        
    # Ajout de quelques informations supplémentaires au résultat
    # pour l'interface utilisateur
    if "details" in results:
        details = results["details"]
        
        # Enrichir avec le nom et le titre du profil
        if profile_data.get("full_name"):
            details["nom"] = profile_data.get("full_name")
        else:
            # Tenter d'extraire des parties du nom si disponibles
            first_name = profile_data.get("first_name", "")
            last_name = profile_data.get("last_name", "")
            if first_name or last_name:
                details["nom"] = f"{first_name} {last_name}".strip()
            else:
                details["nom"] = "Non spécifié"
                
        # Ajouter le titre/poste actuel
        if profile_data.get("headline"):
            details["titre"] = profile_data.get("headline")
        else:
            # Tenter d'obtenir le titre du dernier poste
            experiences = profile_data.get("experiences", [])
            if experiences:
                for exp in experiences:
                    if exp.get("starts_at") is None or exp.get("ends_at") is None:
                        if exp.get("title"):
                            details["titre"] = exp.get("title")
                            if exp.get("company") and exp.get("company", {}).get("name"):
                                details["titre"] += f" chez {exp.get('company', {}).get('name', '')}"
                            break
            if "titre" not in details:
                details["titre"] = "Non spécifié"
    
    # Ajouter les pondérations utilisées pour le calcul du score
    results["ponderations"] = {
        "experience": int(exp_weight * 100),
        "education": int(edu_weight * 100),
        "secteur": int(sector_weight * 100)
    }
    
    # Ajouter l'URL pour référence
    results["url"] = linkedin_url
    
    return results

def main():
    """
    Fonction principale pour extraire les données LinkedIn et réaliser le scoring
    """
    if len(sys.argv) < 2:
        print("Usage: python scrape_linkedin.py <url_profil_linkedin>")
        sys.exit(1)
    
    linkedin_url = sys.argv[1]
    
    try:
        # Utiliser la nouvelle fonction process_linkedin_profile
        results = process_linkedin_profile(linkedin_url)
        
        # Affichage des résultats
        print("\n===== RÉSULTATS DU SCORING =====")
        print(f"Score: {results.get('score', 0)}/10")
        print(f"Justification: {results.get('justification', 'Non fournie')}")
        
        if "details" in results:
            details = results["details"]
            print("\nDétails de l'analyse:")
            print(f"- Nom: {details.get('nom', 'Non déterminé')}")
            print(f"- Titre: {details.get('titre', 'Non déterminé')}")
            print(f"- Années d'expérience: {details.get('experience_annees', 'Non déterminé')}")
            print(f"- Niveau d'éducation: {details.get('niveau_education', 'Non déterminé')}")
            print(f"- Secteur d'activité: {details.get('secteur_activite', 'Non déterminé')}")
        
        # Affichage du raisonnement complet si disponible
        if "raisonnement" in results:
            print("\nRaisonnement détaillé de Gemini:")
            print(results["raisonnement"])
        
        # Sortie JSON complète pour intégration
        print("\nJSON complet:")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"\n[ERREUR] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 