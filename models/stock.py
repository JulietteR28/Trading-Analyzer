"""
Classe Stock - Représente une action boursière
"""
from datetime import datetime
from typing import Optional


class Stock:
    """
    Classe représentant une action boursière avec ses données principales
    
    Attributes:
        symbol (str): Symbole boursier de l'action (ex: 'AAPL' pour Apple)
        name (str): Nom complet de l'entreprise (ex: 'Apple Inc.')
        current_price (float): Prix actuel de l'action
        opening_price (float): Prix d'ouverture du jour
        highest_price (float): Prix le plus haut du jour
        lowest_price (float): Prix le plus bas du jour
        volume (int): Volume d'échanges du jour
        last_update (datetime): Date et heure de la dernière mise à jour
    """
    
    def __init__(self, symbol: str, name: str):
        """
        Initialise une nouvelle instance de Stock
        
        Args:
            symbol (str): Symbole boursier (ex: 'AAPL')
            name (str): Nom de l'entreprise (ex: 'Apple Inc.')
        """
        self.symbol = symbol.upper()  # Toujours en majuscules
        self.name = name
        self.current_price: Optional[float] = None
        self.opening_price: Optional[float] = None
        self.highest_price: Optional[float] = None
        self.lowest_price: Optional[float] = None
        self.volume: Optional[int] = None
        self.last_update: Optional[datetime] = None
    
    def update_price(self, new_price: float, 
                     opening: Optional[float] = None,
                     high: Optional[float] = None, 
                     low: Optional[float] = None,
                     volume: Optional[int] = None):
        """
        Met à jour les informations de prix de l'action
        
        Args:
            new_price (float): Nouveau prix actuel
            opening (float, optional): Prix d'ouverture
            high (float, optional): Prix le plus haut
            low (float, optional): Prix le plus bas
            volume (int, optional): Volume d'échanges
        """
        self.current_price = new_price
        if opening is not None:
            self.opening_price = opening
        if high is not None:
            self.highest_price = high
        if low is not None:
            self.lowest_price = low
        if volume is not None:
            self.volume = volume
        self.last_update = datetime.now()
    
    def get_variation(self) -> Optional[float]:
        """
        Calcule la variation en pourcentage depuis l'ouverture
        
        Returns:
            float: Variation en % (ex: 2.5 pour +2.5%), ou None si données manquantes
        """
        if self.current_price is None or self.opening_price is None:
            return None
        
        if self.opening_price == 0:  # Éviter division par zéro
            return None
        
        variation = ((self.current_price - self.opening_price) / self.opening_price) * 100
        return round(variation, 2)
    
    def get_variation_value(self) -> Optional[float]:
        """
        Calcule la variation en valeur absolue depuis l'ouverture
        
        Returns:
            float: Variation en $ (ex: 3.45 pour +$3.45), ou None si données manquantes
        """
        if self.current_price is None or self.opening_price is None:
            return None
        
        return round(self.current_price - self.opening_price, 2)
    
    def to_dict(self) -> dict:
        """
        Convertit l'objet Stock en dictionnaire
        Utile pour la sérialisation (sauvegarde, API, etc.)
        
        Returns:
            dict: Dictionnaire contenant toutes les informations de l'action
        """
        return {
            'symbol': self.symbol,
            'name': self.name,
            'current_price': self.current_price,
            'opening_price': self.opening_price,
            'highest_price': self.highest_price,
            'lowest_price': self.lowest_price,
            'volume': self.volume,
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'variation_percent': self.get_variation(),
            'variation_value': self.get_variation_value()
        }
    
    def __str__(self) -> str:
        """
        Représentation textuelle de l'action (pour print())
        
        Returns:
            str: Description de l'action
        """
        variation = self.get_variation()
        variation_str = f"{variation:+.2f}%" if variation is not None else "N/A"
        price_str = f"${self.current_price:.2f}" if self.current_price else "N/A"
        
        return f"{self.symbol} ({self.name}) - Prix: {price_str} | Variation: {variation_str}"
    
    def __repr__(self) -> str:
        """
        Représentation technique de l'action (pour debug)
        
        Returns:
            str: Représentation de l'objet
        """
        return f"Stock(symbol='{self.symbol}', name='{self.name}', price={self.current_price})"