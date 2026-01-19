"""
Module DataFetcher - Récupération de données boursières via API
Implémenté avec yfinance
"""
from typing import Dict, Optional, List
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
from models.stock import Stock


class DataFetcher:
    """
    Classe responsable de la récupération de données depuis les APIs boursières
    
    API principale: yfinance (gratuite, sans clé requise)
    
    Attributes:
        cache (dict): Cache simple pour éviter les appels répétés
    """
    
    def __init__(self):
        """Initialise le DataFetcher"""
        self.cache = {}
        print("DataFetcher initialisé avec yfinance")
    
    def fetch_current_price(self, symbol: str) -> Optional[Dict]:
        """
        Récupère le prix actuel d'une action avec yfinance
        
        Args:
            symbol (str): Symbole boursier (ex: 'AAPL')
        
        Returns:
            dict: Données de l'action ou None si erreur
                {
                    'symbol': str,
                    'name': str,
                    'current_price': float,
                    'open': float,
                    'high': float,
                    'low': float,
                    'volume': int,
                    'previous_close': float
                }
        """
        try:
            print(f"Récupération des données pour {symbol}...")
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Vérifier si le symbole est valide
            if not info or 'currentPrice' not in info:
                print(f"Symbole {symbol} invalide ou données indisponibles")
                return None
            
            data = {
                'symbol': symbol.upper(),
                'name': info.get('longName', info.get('shortName', symbol)),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice')),
                'open': info.get('open', info.get('regularMarketOpen')),
                'high': info.get('dayHigh', info.get('regularMarketDayHigh')),
                'low': info.get('dayLow', info.get('regularMarketDayLow')),
                'volume': info.get('volume', info.get('regularMarketVolume', 0)),
                'previous_close': info.get('previousClose', info.get('regularMarketPreviousClose'))
            }
            
            print(f"Données récupérées pour {symbol}: ${data['current_price']:.2f}")
            return data
            
        except Exception as e:
            print(f"Erreur lors de la récupération de {symbol}: {e}")
            return None
    
    def fetch_historical_data(self, 
                             symbol: str, 
                             period: str = "1mo",
                             interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Récupère l'historique des prix d'une action
        
        Args:
            symbol (str): Symbole boursier
            period (str): Période ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
            interval (str): Intervalle ('1m', '5m', '1h', '1d', '1wk', '1mo')
        
        Returns:
            DataFrame: Historique avec colonnes [Date, Open, High, Low, Close, Volume]
                      ou None si erreur
        """
        try:
            print(f"Récupération historique {symbol} ({period}, intervalle {interval})...")
            
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                print(f"Aucune donnée historique pour {symbol}")
                return None
            
            # Réinitialiser l'index pour avoir Date comme colonne
            hist = hist.reset_index()
            
            print(f"✅ {len(hist)} entrées récupérées pour {symbol}")
            return hist
            
        except Exception as e:
            print(f"Erreur lors de la récupération historique de {symbol}: {e}")
            return None
    
    def update_stock_from_api(self, stock: Stock) -> bool:
        """
        Met à jour un objet Stock avec les données de l'API
        
        Args:
            stock (Stock): Objet Stock à mettre à jour
        
        Returns:
            bool: True si succès, False sinon
        """
        try:
            data = self.fetch_current_price(stock.symbol)
            
            if data is None:
                return False
            
            # Mettre à jour le nom si pas déjà défini
            if stock.name == stock.symbol or not stock.name:
                stock.name = data['name']
            
            # Mettre à jour les prix
            stock.update_price(
                new_price=data['current_price'],
                opening=data['open'],
                high=data['high'],
                low=data['low'],
                volume=data['volume']
            )
            
            print(f" Stock {stock.symbol} mis à jour avec succès")
            return True
            
        except Exception as e:
            print(f" Erreur lors de la mise à jour de {stock.symbol}: {e}")
            return False
    
    def create_stock_from_api(self, symbol: str) -> Optional[Stock]:
        """
        Crée un nouvel objet Stock à partir des données API
        
        Args:
            symbol (str): Symbole boursier
        
        Returns:
            Stock: Objet Stock créé et rempli, ou None si erreur
        """
        try:
            data = self.fetch_current_price(symbol)
            
            if data is None:
                return None
            
            # Créer le stock
            stock = Stock(symbol=data['symbol'], name=data['name'])
            
            # Remplir avec les données
            stock.update_price(
                new_price=data['current_price'],
                opening=data['open'],
                high=data['high'],
                low=data['low'],
                volume=data['volume']
            )
            
            print(f"✅ Stock {symbol} créé avec succès")
            return stock
            
        except Exception as e:
            print(f" Erreur lors de la création du stock {symbol}: {e}")
            return None
    
    def fetch_multiple_stocks_sync(self, symbols: List[str]) -> List[Stock]:
        """
        Récupère plusieurs actions de manière synchrone (une par une)
        Utile pour comparer avec la version asynchrone
        
        Args:
            symbols (List[str]): Liste de symboles boursiers
        
        Returns:
            List[Stock]: Liste des stocks créés (peut être partielle si erreurs)
        """
        stocks = []
        
        print(f" Récupération synchrone de {len(symbols)} actions...")
        start_time = datetime.now()
        
        for symbol in symbols:
            stock = self.create_stock_from_api(symbol)
            if stock:
                stocks.append(stock)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f" Temps écoulé (sync): {elapsed:.2f}s pour {len(stocks)}/{len(symbols)} actions")
        
        return stocks
    
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        Récupère des informations détaillées sur une action
        
        Args:
            symbol (str): Symbole boursier
        
        Returns:
            dict: Informations complètes (secteur, industrie, capitalisation, etc.)
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'symbol': symbol.upper(),
                'name': info.get('longName', ''),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0),
                'website': info.get('website', ''),
                'description': info.get('longBusinessSummary', '')
            }
            
        except Exception as e:
            print(f" Erreur lors de la récupération des infos de {symbol}: {e}")
            return None