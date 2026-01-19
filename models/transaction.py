"""
Classe Transaction - Représente une transaction d'achat ou de vente d'actions
"""
from datetime import datetime
from enum import Enum
from typing import Optional


class TransactionType(Enum):
    """Type de transaction"""
    BUY = "ACHAT"
    SELL = "VENTE"


class Transaction:
    """
    Classe représentant une transaction boursière
    
    Attributes:
        transaction_id (int): Identifiant unique de la transaction
        stock_symbol (str): Symbole de l'action concernée
        transaction_type (TransactionType): Type (achat ou vente)
        quantity (int): Nombre d'actions
        price_per_share (float): Prix unitaire de l'action
        transaction_date (datetime): Date et heure de la transaction
        fees (float): Frais de transaction
    """
    
    def __init__(self, 
                 stock_symbol: str,
                 transaction_type: TransactionType,
                 quantity: int,
                 price_per_share: float,
                 transaction_date: Optional[datetime] = None,
                 fees: float = 0.0):
        """
        Initialise une nouvelle transaction
        
        Args:
            stock_symbol (str): Symbole de l'action (ex: 'AAPL')
            transaction_type (TransactionType): BUY ou SELL
            quantity (int): Nombre d'actions (doit être positif)
            price_per_share (float): Prix unitaire (doit être positif)
            transaction_date (datetime, optional): Date de la transaction (défaut: maintenant)
            fees (float): Frais de transaction (défaut: 0.0)
        
        Raises:
            ValueError: Si quantity ou price_per_share sont négatifs
        """
        if quantity <= 0:
            raise ValueError("La quantité doit être positive")
        if price_per_share <= 0:
            raise ValueError("Le prix par action doit être positif")
        
        self.transaction_id: Optional[int] = None  # Sera défini lors de l'insertion en BDD
        self.stock_symbol = stock_symbol.upper()
        self.transaction_type = transaction_type
        self.quantity = quantity
        self.price_per_share = price_per_share
        self.transaction_date = transaction_date or datetime.now()
        self.fees = fees
    
    def get_total_amount(self) -> float:
        """
        Calcule le montant total de la transaction (prix × quantité + frais)
        
        Returns:
            float: Montant total
        """
        return (self.quantity * self.price_per_share) + self.fees
    
    def get_net_amount(self) -> float:
        """
        Calcule le montant net selon le type de transaction
        Pour un ACHAT: montant négatif (sortie d'argent)
        Pour une VENTE: montant positif (entrée d'argent)
        
        Returns:
            float: Montant net (positif ou négatif)
        """
        total = self.get_total_amount()
        return -total if self.transaction_type == TransactionType.BUY else total
    
    def is_buy(self) -> bool:
        """Vérifie si c'est un achat"""
        return self.transaction_type == TransactionType.BUY
    
    def is_sell(self) -> bool:
        """Vérifie si c'est une vente"""
        return self.transaction_type == TransactionType.SELL
    
    def to_dict(self) -> dict:
        """
        Convertit la transaction en dictionnaire
        
        Returns:
            dict: Dictionnaire avec toutes les informations
        """
        return {
            'transaction_id': self.transaction_id,
            'stock_symbol': self.stock_symbol,
            'transaction_type': self.transaction_type.value,
            'quantity': self.quantity,
            'price_per_share': self.price_per_share,
            'total_amount': self.get_total_amount(),
            'fees': self.fees,
            'transaction_date': self.transaction_date.isoformat(),
            'net_amount': self.get_net_amount()
        }
    
    def __str__(self) -> str:
        """
        Représentation textuelle de la transaction
        
        Returns:
            str: Description de la transaction
        """
        action = "ACHAT" if self.is_buy() else "VENTE"
        total = self.get_total_amount()
        date_str = self.transaction_date.strftime("%Y-%m-%d %H:%M")
        
        return (f"{action} de {self.quantity} {self.stock_symbol} "
                f"@ ${self.price_per_share:.2f} = ${total:.2f} "
                f"({date_str})")
    
    def __repr__(self) -> str:
        """
        Représentation technique de la transaction
        
        Returns:
            str: Représentation de l'objet
        """
        return (f"Transaction(symbol='{self.stock_symbol}', "
                f"type={self.transaction_type.value}, "
                f"qty={self.quantity}, "
                f"price=${self.price_per_share})")


# Exemple d'utilisation (pour tester la classe)
if __name__ == "__main__":
    print("=== Tests de la classe Transaction ===\n")
    
    # Créer un achat
    achat = Transaction(
        stock_symbol="AAPL",
        transaction_type=TransactionType.BUY,
        quantity=10,
        price_per_share=175.50,
        fees=5.00
    )
    
    print(f"Transaction 1: {achat}")
    print(f"Montant total: ${achat.get_total_amount():.2f}")
    print(f"Montant net: ${achat.get_net_amount():.2f}")
    print(f"Est un achat? {achat.is_buy()}")
    
    # Créer une vente
    vente = Transaction(
        stock_symbol="GOOGL",
        transaction_type=TransactionType.SELL,
        quantity=5,
        price_per_share=142.30,
        fees=3.50
    )
    
    print(f"\nTransaction 2: {vente}")
    print(f"Montant total: ${vente.get_total_amount():.2f}")
    print(f"Montant net: ${vente.get_net_amount():.2f}")
    print(f"Est une vente? {vente.is_sell()}")
    
    # Afficher en dictionnaire
    print(f"\nDictionnaire: {achat.to_dict()}")
    
    # Test d'erreur
    try:
        mauvaise = Transaction("TSLA", TransactionType.BUY, -5, 200.0)
    except ValueError as e:
        print(f"\n Erreur attendue: {e}")