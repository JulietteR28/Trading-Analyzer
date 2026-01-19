"""
Dictionnaire des actions populaires
Permet la recherche par nom ou symbole
"""

# Dictionnaire: Nom -> Symbole
ACTIONS_DICT = {
    # Tech Giants
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Alphabet": "GOOGL",
    "Amazon": "AMZN",
    "Meta": "META",
    "Facebook": "META",
    "Tesla": "TSLA",
    "Nvidia": "NVDA",
    "Netflix": "NFLX",
    
    # Tech Companies
    "Adobe": "ADBE",
    "Intel": "INTC",
    "AMD": "AMD",
    "Salesforce": "CRM",
    "Oracle": "ORCL",
    "IBM": "IBM",
    "Cisco": "CSCO",
    "PayPal": "PYPL",
    "Uber": "UBER",
    "Lyft": "LYFT",
    "Airbnb": "ABNB",
    "Snap": "SNAP",
    "Twitter": "TWTR",
    "Spotify": "SPOT",
    "Zoom": "ZM",
    "Shopify": "SHOP",
    "Square": "SQ",
    "Block": "SQ",
    "Roku": "ROKU",
    "Roblox": "RBLX",
    
    # Finance
    "JPMorgan": "JPM",
    "Bank of America": "BAC",
    "Wells Fargo": "WFC",
    "Goldman Sachs": "GS",
    "Morgan Stanley": "MS",
    "Citigroup": "C",
    "American Express": "AXP",
    "Visa": "V",
    "Mastercard": "MA",
    "BlackRock": "BLK",
    
    # Retail & Consumer
    "Walmart": "WMT",
    "Target": "TGT",
    "Costco": "COST",
    "Nike": "NKE",
    "Adidas": "ADDYY",
    "Starbucks": "SBUX",
    "McDonald's": "MCD",
    "Coca-Cola": "KO",
    "PepsiCo": "PEP",
    "Procter & Gamble": "PG",
    "Johnson & Johnson": "JNJ",
    
    # Automotive
    "Ford": "F",
    "General Motors": "GM",
    "Ferrari": "RACE",
    "Toyota": "TM",
    "Honda": "HMC",
    "Volkswagen": "VWAGY",
    "BMW": "BMWYY",
    
    # Energy
    "ExxonMobil": "XOM",
    "Chevron": "CVX",
    "Shell": "SHEL",
    "BP": "BP",
    "TotalEnergies": "TTE",
    
    # Aerospace
    "Boeing": "BA",
    "Airbus": "EADSY",
    "Lockheed Martin": "LMT",
    "SpaceX": None,  # Pas cotée
    
    # Pharmaceutical
    "Pfizer": "PFE",
    "Moderna": "MRNA",
    "AstraZeneca": "AZN",
    "Novartis": "NVS",
    "Merck": "MRK",
    
    # Luxury
    "LVMH": "LVMUY",
    "Hermès": "HESAY",
    "Kering": "PPRUY",
    
    # French CAC40
    "Total": "TTE",
    "TotalEnergies": "TTE",
    "LVMH": "LVMUY",
    "Sanofi": "SNY",
    "L'Oréal": "LRLCY",
    "Air Liquide": "AIQUY",
    "BNP Paribas": "BNPQY",
    "Airbus": "EADSY",
    "Danone": "DANOY",
    "Michelin": "MGDDY",
    "Renault": "RNLSY",
    "Peugeot": "PUGOY",
    "Carrefour": "CRRFY",
    "Orange": "ORAN",
    "Veolia": "VEOEY",
}

# Liste pour l'autocomplétion (triée)
ACTIONS_LISTE = sorted([nom for nom in ACTIONS_DICT.keys() if ACTIONS_DICT[nom] is not None])

# Fonction de recherche
def rechercher_action(nom_ou_symbole: str) -> str:
    """
    Recherche une action par nom ou symbole
    
    Args:
        nom_ou_symbole (str): Nom (ex: "Apple") ou symbole (ex: "AAPL")
    
    Returns:
        str: Symbole de l'action ou None si introuvable
    """
    recherche = nom_ou_symbole.strip()
    
    # D'abord chercher par nom (insensible à la casse)
    for nom, symbole in ACTIONS_DICT.items():
        if nom.lower() == recherche.lower():
            return symbole
    
    # Sinon, considérer que c'est déjà un symbole
    return recherche.upper()


# Test
if __name__ == "__main__":
    print("=" * 60)
    print("Test du dictionnaire d'actions")
    print("=" * 60)
    
    tests = ["Apple", "AAPL", "google", "MSFT", "tesla", "amazon"]
    
    for test in tests:
        resultat = rechercher_action(test)
        print(f"{test:20} -> {resultat}")
    
    print(f"\nNombre d'actions disponibles: {len(ACTIONS_LISTE)}")
    print(f"\nPremières actions: {ACTIONS_LISTE[:10]}")