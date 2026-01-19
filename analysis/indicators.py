"""
Module TechnicalIndicators - Indicateurs techniques
"""
import pandas as pd
import numpy as np
from typing import Optional


class TechnicalIndicators:
    """
    Classe pour calculer des indicateurs techniques
    Version adaptée au niveau M1
    
    Indicateurs implémentés:
    - RSI (Relative Strength Index)
    - Signal de trading basique
    """
    
    def __init__(self, data: Optional[pd.DataFrame] = None):
        """
        Initialise TechnicalIndicators
        
        Args:
            data (DataFrame): Données historiques (Date, Close, etc.)
        """
        self.data = data
        print("TechnicalIndicators initialisé")
    
    def set_data(self, data: pd.DataFrame):
        """Met à jour les données"""
        self.data = data
    
    def calculate_rsi(self, period: int = 14) -> Optional[float]:
        """
        Calcule le RSI
        
        Le RSI mesure si une action est "surachetée" ou "survendue":
        - RSI > 70: Peut-être trop cher (suracheté)
        - RSI < 30: Peut-être pas cher (survendu)
        - RSI entre 30-70: Normal
        
        Args:
            period (int): Nombre de jours (défaut: 14)
        
        Returns:
            float: Valeur du RSI (0-100)
        """
        if self.data is None or self.data.empty:
            print("Pas de données")
            return None
        
        # Calculer les variations
        delta = self.data['Close'].diff()
        
        # Séparer les hausses et les baisses
        gains = delta.where(delta > 0, 0)  # Garder seulement les gains
        losses = -delta.where(delta < 0, 0)  # Garder seulement les pertes
        
        # Moyennes des gains et pertes sur N jours
        avg_gain = gains.rolling(window=period).mean().iloc[-1]
        avg_loss = losses.rolling(window=period).mean().iloc[-1]
        
        # Pas de division par 0
        if avg_loss == 0:
            rsi = 100
        else:
            # Formule du RSI
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
        
        print(f"✅ RSI calculé: {rsi:.2f}")
        return rsi
    
    def get_simple_signal(self) -> str:
        """
        Génère un signal de trading simple basé sur le RSI
        
        - RSI < 30: Signal d'ACHAT (action pas chère)
        - RSI > 70: Signal de VENTE (action chère)
        - Sinon: ATTENDRE
        
        Returns:
            str: "ACHETER", "VENDRE", ou "ATTENDRE"
        """
        rsi = self.calculate_rsi()
        
        if rsi is None:
            return "INCONNU"
        
        if rsi < 30:
            signal = "ACHETER"
            print(f"Signal: {signal} (RSI bas = pas cher)")
        elif rsi > 70:
            signal = "VENDRE"
            print(f"Signal: {signal} (RSI haut = cher)")
        else:
            signal = "ATTENDRE"
            print(f"Signal: {signal} (RSI normal)")
        
        return signal
    
    def calculate_price_change(self) -> dict:
        """
        Calcule les changements de prix simples
        
        Returns:
            dict: Informations sur les changements de prix
        """
        if self.data is None or self.data.empty:
            print("Pas de données")
            return {}
        
        first_price = self.data['Close'].iloc[0]
        last_price = self.data['Close'].iloc[-1]
        
        # Variation absolue et en %
        change = last_price - first_price
        change_pct = (change / first_price) * 100
        
        result = {
            'prix_debut': first_price,
            'prix_fin': last_price,
            'variation': change,
            'variation_pct': change_pct
        }
        
        print(f"Variation: {change_pct:+.2f}%")
        return result