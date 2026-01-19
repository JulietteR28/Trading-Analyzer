"""
Module AsyncFetcher - Récupération asynchrone de données boursières
Implémenté avec asyncio pour des performances optimales
"""
from typing import List, Dict, Optional
import asyncio
from datetime import datetime
from models.stock import Stock

from api.data_fetcher import DataFetcher


class AsyncFetcher:
    """
    Classe pour récupération asynchrone de données boursières
    
    Permet de récupérer plusieurs actions en parallèle
    Bien plus rapide que la version synchrone pour de nombreuses actions
    
    """
    
    def __init__(self):
        """Initialise l'AsyncFetcher"""
        self.fetcher = DataFetcher()
        print("AsyncFetcher initialisé (mode async)")
    
    async def fetch_one_stock_async(self, symbol: str) -> Optional[Stock]:
        """
        Récupère une action de manière asynchrone
        
        Args:
            symbol (str): Symbole boursier
        
        Returns:
            Stock: Objet Stock créé ou None
        """
        # Simuler un délai réseau
        await asyncio.sleep(0.1)
        
        # Utiliser le fetcher démo (synchrone) mais dans un contexte async
        stock = await asyncio.to_thread(
            self.fetcher.create_stock_from_api,
            symbol
        )
        
        return stock
    
    async def fetch_multiple_stocks(self, symbols: List[str]) -> List[Stock]:
        """
        Récupère plusieurs actions en parallèle (asynchrone)
        
        C'est ici que la magie opère : toutes les requêtes sont lancées
        en même temps au lieu d'attendre l'une après l'autre
        
        Args:
            symbols (List[str]): Liste de symboles boursiers
        
        Returns:
            List[Stock]: Liste des stocks créés
        """
        print(f"Récupération ASYNCHRONE de {len(symbols)} actions...")
        start_time = datetime.now()
        
        # Créer toutes les tâches asynchrones
        tasks = [self.fetch_one_stock_async(symbol) for symbol in symbols]
        
        # Exécuter toutes les tâches en parallèle
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filtrer les résultats (enlever None et les erreurs)
        stocks = [
            result for result in results 
            if result is not None and isinstance(result, Stock)
        ]
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"emps écoulé (ASYNC): {elapsed:.2f}s pour {len(stocks)}/{len(symbols)} actions")
        print(f"   Gain de performance vs synchrone!")
        
        return stocks
    
    async def fetch_and_update_portfolio(self, portfolio) -> bool:
        """
        Met à jour toutes les actions d'un portfolio en parallèle
        
        Args:
            portfolio: Objet Portfolio
        
        Returns:
            bool: True si au moins une action a été mise à jour
        """
        if not portfolio.stocks:
            print("Portfolio vide, rien à mettre à jour")
            return False
        
        symbols = [stock.symbol for stock in portfolio.stocks]
        print(f"Mise à jour asynchrone du portfolio '{portfolio.name}'...")
        
        # Récupérer les nouvelles données
        updated_stocks = await self.fetch_multiple_stocks(symbols)
        
        # Mettre à jour chaque stock du portfolio
        updates = 0
        for updated_stock in updated_stocks:
            existing_stock = portfolio.get_stock(updated_stock.symbol)
            if existing_stock:
                existing_stock.update_price(
                    new_price=updated_stock.current_price,
                    opening=updated_stock.opening_price,
                    high=updated_stock.highest_price,
                    low=updated_stock.lowest_price,
                    volume=updated_stock.volume
                )
                updates += 1
        
        print(f"{updates} actions mises à jour dans le portfolio")
        return updates > 0
    
    def run_async(self, coro):
        """
        Helper pour exécuter une coroutine de manière synchrone
        Utile pour les tests ou l'intégration avec du code synchrone
        
        Args:
            coro: Coroutine à exécuter
        
        Returns:
            Résultat de la coroutine
        """
        return asyncio.run(coro)


# Fonction helper pour faciliter l'utilisation
async def fetch_stocks_async(symbols: List[str]) -> List[Stock]:
    """
    Fonction helper pour récupérer plusieurs actions de manière asynchrone
    
    Args:
        symbols (List[str]): Liste de symboles
    
    Returns:
        List[Stock]: Liste de stocks
    
    Exemple d'utilisation:
        stocks = await fetch_stocks_async(["AAPL", "GOOGL", "MSFT"])
    """
    fetcher = AsyncFetcher()
    return await fetcher.fetch_multiple_stocks(symbols)