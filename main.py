import asyncio
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional

from dotenv import load_dotenv
from src.linkedin_scraper import LinkedInCrawl4AIScraper
from src.scoring_system import ProfileScorer

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('linkedin_agent.log')
    ]
)
logger = logging.getLogger(__name__)

# Chargement des variables d'environnement
load_dotenv()

async def process_profile(url: str) -> Dict:
    """
    Traite un profil LinkedIn: extraction des données et calcul du score
    
    Args:
        url (str): URL du profil LinkedIn
        
    Returns:
        Dict: Résultat complet (données du profil + score)
    """
    try:
        logger.info(f"Traitement du profil: {url}")
        
        # 1. Extraction des données du profil
        scraper = LinkedInCrawl4AIScraper()
        profile_data = await scraper.scrape_profile(url)
        
        if not profile_data:
            logger.error(f"❌ Échec de l'extraction pour {url}")
            return {
                "url": url,
                "error": "Échec de l'extraction des données du profil",
                "timestamp": datetime.now().isoformat()
            }
        
        # 2. Calcul du score
        scorer = ProfileScorer()
        score_result = scorer.calculate_score(profile_data)
        
        # 3. Combinaison des résultats
        result = {
            "url": url,
            "profile_data": profile_data,
            "score_result": score_result,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        
        logger.info(f"✅ Traitement terminé pour {url} - Score: {score_result['scores']['global']}/10")
        return result
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du traitement de {url}: {str(e)}")
        return {
            "url": url,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "success": False
        }

async def process_multiple_profiles(urls: List[str], output_file: Optional[str] = None) -> List[Dict]:
    """
    Traite plusieurs profils LinkedIn en parallèle
    
    Args:
        urls (List[str]): Liste des URLs de profils LinkedIn
        output_file (str, optional): Chemin du fichier de sortie pour les résultats
        
    Returns:
        List[Dict]: Liste des résultats pour chaque profil
    """
    logger.info(f"Traitement de {len(urls)} profils...")
    
    # Création de toutes les tâches pour le traitement en parallèle
    tasks = [process_profile(url) for url in urls]
    
    # Exécution de toutes les tâches de manière concurrente
    results = await asyncio.gather(*tasks)
    
    # Enregistrement des résultats dans un fichier si demandé
    if output_file:
        try:
            # Création du dossier de sortie si nécessaire
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            
            # Enregistrement des résultats
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
            logger.info(f"✅ Résultats enregistrés dans {output_file}")
        except Exception as e:
            logger.error(f"❌ Erreur lors de l'enregistrement des résultats: {str(e)}")
    
    # Statistiques
    success_count = sum(1 for r in results if r.get("success", False))
    error_count = len(results) - success_count
    
    logger.info(f"📊 Bilan: {success_count} profils traités avec succès, {error_count} échecs")
    
    return results

async def main():
    """Fonction principale du script"""
    try:
        # Vérification des arguments de la ligne de commande
        if len(sys.argv) < 2:
            print("Usage:")
            print(f"  1. Traiter un seul profil:  python {sys.argv[0]} <url_linkedin>")
            print(f"  2. Traiter plusieurs profils:  python {sys.argv[0]} --file <chemin_fichier_urls>")
            sys.exit(1)
        
        # Déterminer le mode d'exécution
        if sys.argv[1] == "--file" and len(sys.argv) >= 3:
            # Mode traitement par lot depuis un fichier
            input_file = sys.argv[2]
            output_file = f"output/results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            if not os.path.exists(input_file):
                logger.error(f"❌ Fichier d'entrée introuvable: {input_file}")
                sys.exit(1)
            
            # Lecture des URLs depuis le fichier
            with open(input_file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            # Traitement des profils
            results = await process_multiple_profiles(urls, output_file)
            
            # Affichage des résultats en sortie standard
            print(json.dumps(results, ensure_ascii=False, indent=2))
            
        else:
            # Mode traitement d'un seul profil
            url = sys.argv[1]
            
            # Traitement du profil
            result = await process_profile(url)
            
            # Affichage du résultat en sortie standard
            print(json.dumps(result, ensure_ascii=False, indent=2))
    
    except Exception as e:
        logger.error(f"❌ Erreur globale: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Point d'entrée du programme
    asyncio.run(main()) 