import asyncio
from src.linkedin_scraper import scrape_linkedin_profile

async def test_scraper():
    # URL d'un profil LinkedIn public très connu (Bill Gates)
    url = "https://www.linkedin.com/in/williamhgates/"
    
    print("🔄 Début du test de scraping...")
    result = await scrape_linkedin_profile(url)
    
    if result:
        print("\n✅ Données extraites avec succès :")
        print(f"Nom: {result.get('nom', 'Non trouvé')}")
        print(f"Titre: {result.get('titre', 'Non trouvé')}")
    else:
        print("❌ Échec du scraping")

if __name__ == "__main__":
    asyncio.run(test_scraper()) 