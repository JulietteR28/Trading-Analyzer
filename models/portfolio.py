"""
Classe Portfolio - Gestion d'un portefeuille d'actions
"""
from typing import List, Optional
from models.stock import Stock


class Portfolio:
    """
    Classe représentant un portefeuille d'actions boursières
    
    Attributes:
        name (str): Nom du portefeuille
        stocks (List[Stock]): Liste des actions dans le portefeuille
    """
    
    def __init__(self, name: str = "Mon Portfolio"):
        """
        Initialise un nouveau portfolio
        
        Args:
            name (str): Nom du portefeuille (par défaut "Mon Portfolio")
        """
        self.name = name
        self.stocks: List[Stock] = []
    
    def add_stock(self, stock: Stock) -> bool:
        """
        Ajoute une action au portefeuille
        
        Args:
            stock (Stock): L'action à ajouter
            
        Returns:
            bool: True si ajouté avec succès, False si déjà présent
        """
        # Vérifier si l'action existe dans le portfolio
        if self.get_stock(stock.symbol) is not None:
            print(f" L'action {stock.symbol} est déjà dans le portefeuille")
            return False
        
        self.stocks.append(stock)
        print(f" Action {stock.symbol} ajoutée au portefeuille '{self.name}'")
        return True
    
    def remove_stock(self, symbol: str) -> bool:
        """
        Retire une action du portefeuille par son symbole
        
        Args:
            symbol (str): Symbole de l'action à retirer
            
        Returns:
            bool: True si retiré avec succès, False si non trouvé
        """
        symbol = symbol.upper()
        
        for i, stock in enumerate(self.stocks):
            if stock.symbol == symbol:
                removed_stock = self.stocks.pop(i)
                print(f" Action {removed_stock.symbol} retirée du portefeuille")
                return True
        
        print(f" Action {symbol} non trouvée dans le portefeuille")
        return False
    
    def get_stock(self, symbol: str) -> Optional[Stock]:
        """
        Récupère une action du portefeuille par son symbole
        
        Args:
            symbol (str): Symbole de l'action recherchée
            
        Returns:
            Stock: L'action trouvée, ou None si non trouvée
        """
        symbol = symbol.upper()
        
        for stock in self.stocks:
            if stock.symbol == symbol:
                return stock
        
        return None
    
    def get_total_value(self) -> float:
        """
        Calcule la valeur totale du portefeuille
        Note: Pour simplifier, on considère 1 action de chaque
        Dans une version complète, on ajouterait une quantité par action
        
        Returns:
            float: Valeur totale du portefeuille
        """
        total = 0.0
        
        for stock in self.stocks:
            if stock.current_price is not None:
                total += stock.current_price
        
        return round(total, 2)
    
    def get_best_performer(self) -> Optional[Stock]:
        """
        Trouve l'action avec la meilleure performance (variation %)
        
        Returns:
            Stock: L'action la plus performante, ou None si portfolio vide
        """
        if not self.stocks:
            return None
        
        best_stock = None
        best_variation = float('-inf')  # Commence à -infini
        
        for stock in self.stocks:
            variation = stock.get_variation()
            if variation is not None and variation > best_variation:
                best_variation = variation
                best_stock = stock
        
        return best_stock
    
    def get_worst_performer(self) -> Optional[Stock]:
        """
        Trouve l'action avec la moins bonne performance (variation %)
        
        Returns:
            Stock: L'action la moins performante, ou None si portfolio vide
        """
        if not self.stocks:
            return None
        
        worst_stock = None
        worst_variation = float('inf')  # Commence à +infini
        
        for stock in self.stocks:
            variation = stock.get_variation()
            if variation is not None and variation < worst_variation:
                worst_variation = variation
                worst_stock = stock
        
        return worst_stock
    
    def get_stocks_count(self) -> int:
        """
        Retourne le nombre d'actions dans le portefeuille
        
        Returns:
            int: Nombre d'actions
        """
        return len(self.stocks)
    
    def get_average_variation(self) -> Optional[float]:
        """
        Calcule la variation moyenne de toutes les actions
        
        Returns:
            float: Variation moyenne en %, ou None si aucune donnée
        """
        if not self.stocks:
            return None
        
        variations = []
        for stock in self.stocks:
            var = stock.get_variation()
            if var is not None:
                variations.append(var)
        
        if not variations:
            return None
        
        return round(sum(variations) / len(variations), 2)
    
    def to_dict(self) -> dict:
        """
        Convertit le portfolio en dictionnaire
        
        Returns:
            dict: Dictionnaire contenant les informations du portfolio
        """
        return {
            'name': self.name,
            'stocks_count': self.get_stocks_count(),
            'total_value': self.get_total_value(),
            'average_variation': self.get_average_variation(),
            'stocks': [stock.to_dict() for stock in self.stocks]
        }
    
    def __str__(self) -> str:
        """
        Représentation textuelle du portfolio
        
        Returns:
            str: Description du portfolio
        """
        count = self.get_stocks_count()
        total = self.get_total_value()
        avg_var = self.get_average_variation()
        avg_var_str = f"{avg_var:+.2f}%" if avg_var else "N/A"
        
        return (f"Portfolio '{self.name}': {count} actions | "
                f"Valeur: ${total:.2f} | Variation moy.: {avg_var_str}")
    
    def __repr__(self) -> str:
        """
        Représentation technique du portfolio
        
        Returns:
            str: Représentation de l'objet
        """
        return f"Portfolio(name='{self.name}', stocks={len(self.stocks)})"