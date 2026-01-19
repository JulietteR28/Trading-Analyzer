"""
Module ChartGenerator - Generation de graphiques
"""
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Optional
import pandas as pd


class ChartGenerator:
    """
    Classe pour creer des graphiques
    
    Graphiques disponibles:
    - Graphique de prix
    - Graphique avec moyenne mobile
    - Comparaison de plusieurs actions
    """
    
    def __init__(self):
        """Initialise le ChartGenerator"""
        # Configuration du style
        plt.style.use('default')
        print(" ChartGenerator initialise")
    
    def create_price_chart(self, data: pd.DataFrame, title: str = "Prix de l'action") -> plt.Figure:
        """
        Cree un graphique simple des prix
        
        Args:
            data (DataFrame): Donnees avec colonnes Date et Close
            title (str): Titre du graphique
        
        Returns:
            Figure: Graphique matplotlib
        """
        print(f"  Creation du graphique: {title}")
        
        # Creer la figure avec taille TRES reduite pour PDF
        fig, ax = plt.subplots(figsize=(8, 3))
        
        # Tracer la ligne des prix
        ax.plot(data['Date'], data['Close'], color='blue', linewidth=2, label='Prix')
        
        # Personnalisation
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Prix ($)', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Formater les dates sur l'axe X
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        print("   Graphique cree")
        
        return fig
    
    def create_price_with_ma(self, data: pd.DataFrame, ma: pd.Series, 
                            title: str = "Prix avec Moyenne Mobile",
                            window: int = 20) -> plt.Figure:
        """
        Cree un graphique avec prix et moyenne mobile
        
        Args:
            data (DataFrame): Donnees avec Date et Close
            ma (Series): Moyenne mobile
            title (str): Titre du graphique
            window (int): Periode de la moyenne mobile
        
        Returns:
            Figure: Graphique matplotlib
        """
        print(f"  Creation du graphique: {title}")
        
        # Creer la figure
        fig, ax = plt.subplots(figsize=(8, 3))
        
        # Tracer le prix
        ax.plot(data['Date'], data['Close'], color='blue', linewidth=2, label='Prix')
        
        # Tracer la moyenne mobile
        ax.plot(data['Date'], ma, color='red', linewidth=2, 
                linestyle='--', label=f'Moyenne Mobile ({window}j)')
        
        # Personnalisation
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Prix ($)', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Formater les dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        print("   Graphique cree")
        
        return fig
    
    def create_comparison_chart(self, stocks_data: dict, 
                               title: str = "Comparaison des actions") -> plt.Figure:
        """
        Compare plusieurs actions sur un meme graphique
        
        Args:
            stocks_data (dict): {symbol: DataFrame} pour chaque action
            title (str): Titre du graphique
        
        Returns:
            Figure: Graphique matplotlib
        """
        print(f"  Creation du graphique: {title}")
        
        # Creer la figure
        fig, ax = plt.subplots(figsize=(8, 3))
        
        # Couleurs pour chaque action
        colors = ['blue', 'green', 'red', 'orange', 'purple']
        
        # Tracer chaque action
        for i, (symbol, data) in enumerate(stocks_data.items()):
            color = colors[i % len(colors)]
            
            # Normaliser les prix pour comparaison (base 100)
            first_price = data['Close'].iloc[0]
            normalized = (data['Close'] / first_price) * 100
            
            ax.plot(data['Date'], normalized, color=color, 
                   linewidth=2, label=symbol)
        
        # Personnalisation
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Prix normalise (base 100)', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Ligne horizontale a 100
        ax.axhline(y=100, color='gray', linestyle=':', alpha=0.5)
        
        # Formater les dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        print("   Graphique cree")
        
        return fig
    
    def create_volume_chart(self, data: pd.DataFrame, 
                           title: str = "Volume de transactions") -> plt.Figure:
        """
        Cree un graphique des volumes
        
        Args:
            data (DataFrame): Donnees avec Date et Volume
            title (str): Titre du graphique
        
        Returns:
            Figure: Graphique matplotlib
        """
        print(f"  Creation du graphique: {title}")
        
        # Creer la figure
        fig, ax = plt.subplots(figsize=(8, 2.5))
        
        # Graphique en barres pour les volumes
        ax.bar(data['Date'], data['Volume'], color='lightblue', 
               alpha=0.7, label='Volume')
        
        # Personnalisation
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Volume', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        # Formater les dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        print("   Graphique cree")
        
        return fig
    
    def save_chart(self, fig: plt.Figure, filename: str):
        """
        Sauvegarde un graphique
        
        Args:
            fig (Figure): Figure a sauvegarder
            filename (str): Nom du fichier (ex: 'mon_graphique.png')
        """
        filepath = f"data/exports/{filename}"
        fig.savefig(filepath, dpi=300, bbox_inches='tight')
        print(f"   Graphique sauvegarde: {filepath}")
    
    def show_chart(self, fig: plt.Figure):
        """
        Affiche un graphique a l'ecran
        
        Args:
            fig (Figure): Figure a afficher
        """
        plt.show()
    
    def close_all(self):
        """Ferme tous les graphiques"""
        plt.close('all')