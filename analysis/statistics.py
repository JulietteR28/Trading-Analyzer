"""
Module Analyzer - Analyse statistique des données boursières
"""
import numpy as np
import pandas as pd
from typing import Optional


class Analyzer:
    """
    Classe pour analyser des données boursières
    
    Attributes:
        data (DataFrame): Données historiques à analyser
    """
    
    def __init__(self, data: Optional[pd.DataFrame] = None):
        """
        Initialise l'Analyzer
        
        Args:
            data (DataFrame): DataFrame avec colonnes Date, Open, High, Low, Close, Volume
        """
        self.data = data
        print("Analyzer initialisé")
    
    def set_data(self, data: pd.DataFrame):
        """Met à jour les données"""
        self.data = data
    
    def calculate_moving_average(self, window: int = 20) -> Optional[pd.Series]:
        """
        Calcule la moyenne mobile simple
        
        Moyenne mobile = moyenne des N derniers jours
        Exemple: MA-20 = moyenne des 20 derniers prix
        
        Args:
            window (int): Nombre de jours (défaut: 20)
        
        Returns:
            Series: Moyenne mobile
        """
        if self.data is None or self.data.empty:
            print("Pas de données")
            return None
        
        # Utiliser pandas rolling pour calculer la moyenne
        ma = self.data['Close'].rolling(window=window).mean()
        print(f"Moyenne mobile sur {window} jours calculée")
        return ma
    
    def calculate_daily_return(self) -> Optional[pd.Series]:
        """
        Calcule les variations quotidiennes en %
        
        Variation = ((Prix aujourd'hui - Prix hier) / Prix hier) * 100
        
        Returns:
            Series: Variations en %
        """
        if self.data is None or self.data.empty:
            print("Pas de données")
            return None
        
        returns = self.data['Close'].pct_change() * 100
        print("Variations quotidiennes calculées")
        return returns
    
    def calculate_volatility(self) -> Optional[float]:
        """
        Calcule la volatilité = écart-type des variations
        
        Plus la volatilité est haute, plus le prix bouge beaucoup
        
        Returns:
            float: Volatilité en %
        """
        returns = self.calculate_daily_return()
        if returns is None:
            return None
        
        # Écart-type = mesure de dispersion
        volatility = returns.std()
        print(f"Volatilité: {volatility:.2f}%")
        return volatility
    
    def get_statistics(self) -> dict:
        """
        Calcule des statistiques simples sur les prix
        
        Returns:
            dict: Statistiques de base
        """
        if self.data is None or self.data.empty:
            print("Pas de données")
            return {}
        
        prices = self.data['Close']
        
        stats = {
            'prix_moyen': prices.mean(),
            'prix_min': prices.min(),
            'prix_max': prices.max(),
            'ecart_type': prices.std()
        }
        
        print("Statistiques calculées")
        return stats
    
    def calculate_trend(self, window: int = 20) -> str:
        """
        Détermine si le prix est en hausse ou en baisse
        
        Compare le prix actuel avec la moyenne mobile
        
        Args:
            window (int): Nombre de jours pour la moyenne
        
        Returns:
            str: "HAUSSE", "BAISSE", ou "STABLE"
        """
        if self.data is None or self.data.empty:
            print("Pas de données")
            return "INCONNU"
        
        # Prix actuel
        current_price = self.data['Close'].iloc[-1]
        
        # Moyenne mobile
        ma = self.calculate_moving_average(window)
        if ma is None:
            return "INCONNU"
        
        ma_value = ma.iloc[-1]
        
        if current_price > ma_value * 1.02:  # 2% au-dessus
            trend = "HAUSSE"
        elif current_price < ma_value * 0.98:  # 2% en-dessous
            trend = "BAISSE"
        else:
            trend = "STABLE"
        
        print(f"✅ Tendance: {trend}")
        return trend