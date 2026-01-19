"""
Classe DatabaseManager - Gestion de la base de données SQLite
"""
import sqlite3
from typing import List, Optional, Tuple
from datetime import datetime, date
import os


class DatabaseManager:
    """
    Classe responsable de toutes les interactions avec la base de données
    
    Attributes:
        db_path (str): Chemin vers le fichier de base de données
        connection (sqlite3.Connection): Connexion à la base de données
    """
    
    def __init__(self, db_path: str = "data/stocks.db"):
        """
        Initialise la connexion à la base de données
        
        Args:
            db_path (str): Chemin vers le fichier .db
        """
        self.db_path = db_path
        self.connection: Optional[sqlite3.Connection] = None
        
        # Créer le dossier data s'il n'existe pas
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Se connecter à la base de données
        self._connect()
        
        # Créer les tables si elles n'existent pas
        self.create_tables()
    
    def _connect(self):
        """
        Établit la connexion à la base de données SQLite
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.execute("PRAGMA foreign_keys = ON")
            print(f"Connexion établie à la base de données: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Erreur de connexion à la base de données: {e}")
            raise
    
    def create_tables(self):
        """
        Crée toutes les tables nécessaires à partir du fichier schema.sql
        """
        try:
            # Lire le fichier schema.sql
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            
            with open(schema_path, 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Exécuter le script SQL
            self.connection.executescript(schema_sql)
            self.connection.commit()
            print("Tables créées avec succès")
            
        except FileNotFoundError:
            print("Fichier schema.sql non trouvé, création manuelle des tables...")
            self._create_tables_manually()
        except sqlite3.Error as e:
            print(f"Erreur lors de la création des tables: {e}")
            raise
    
    def _create_tables_manually(self):
        """
        Crée les tables manuellement si schema.sql n'est pas trouvé
        """
        cursor = self.connection.cursor()
        
        # Table stocks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Table stock_prices
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_id INTEGER NOT NULL,
                date DATE NOT NULL,
                opening_price REAL NOT NULL,
                closing_price REAL NOT NULL,
                highest_price REAL NOT NULL,
                lowest_price REAL NOT NULL,
                volume INTEGER NOT NULL,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
                UNIQUE(stock_id, date)
            )
        """)
        
        self.connection.commit()
        print("Tables créées manuellement")
    
    def insert_stock(self, symbol: str, name: str) -> Optional[int]:
        """
        Insert une nouvelle action dans la base de données
        
        Args:
            symbol (str): Symbole boursier
            name (str): Nom de l'entreprise
            
        Returns:
            int: ID de l'action insérée, ou None si erreur
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO stocks (symbol, name) VALUES (?, ?)",
                (symbol.upper(), name)
            )
            self.connection.commit()
            print(f"Action {symbol} ajoutée à la BDD (ID: {cursor.lastrowid})")
            return cursor.lastrowid
            
        except sqlite3.IntegrityError:
            # L'action existe déjà
            print(f"Action {symbol} déjà présente dans la BDD")
            return self.get_stock_id(symbol)
        except sqlite3.Error as e:
            print(f"Erreur lors de l'insertion: {e}")
            return None
    
    def get_stock_id(self, symbol: str) -> Optional[int]:
        """
        Récupère l'ID d'une action par son symbole
        
        Args:
            symbol (str): Symbole boursier
            
        Returns:
            int: ID de l'action, ou None si non trouvée
        """
        cursor = self.connection.cursor()
        cursor.execute(
            "SELECT id FROM stocks WHERE symbol = ?",
            (symbol.upper(),)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    
    def insert_stock_price(self, symbol: str, date_value: date, 
                          opening: float, closing: float,
                          high: float, low: float, volume: int) -> bool:
        """
        Insère les données de prix pour une action à une date donnée
        
        Args:
            symbol (str): Symbole boursier
            date_value (date): Date des données
            opening (float): Prix d'ouverture
            closing (float): Prix de clôture
            high (float): Prix le plus haut
            low (float): Prix le plus bas
            volume (int): Volume d'échanges
            
        Returns:
            bool: True si succès, False sinon
        """
        stock_id = self.get_stock_id(symbol)
        if stock_id is None:
            print(f"Action {symbol} non trouvée dans la BDD")
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                INSERT INTO stock_prices 
                (stock_id, date, opening_price, closing_price, highest_price, lowest_price, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (stock_id, date_value, opening, closing, high, low, volume))
            
            self.connection.commit()
            return True
            
        except sqlite3.IntegrityError:
            # Données déjà présentes pour cette date
            print(f"Données déjà présentes pour {symbol} le {date_value}")
            return False
        except sqlite3.Error as e:
            print(f"Erreur lors de l'insertion des prix: {e}")
            return False
    
    def get_stock_history(self, symbol: str, 
                         start_date: Optional[date] = None,
                         end_date: Optional[date] = None) -> List[Tuple]:
        """
        Récupère l'historique des prix d'une action
        
        Args:
            symbol (str): Symbole boursier
            start_date (date, optional): Date de début
            end_date (date, optional): Date de fin
            
        Returns:
            List[Tuple]: Liste de tuples (date, open, close, high, low, volume)
        """
        stock_id = self.get_stock_id(symbol)
        if stock_id is None:
            return []
        
        cursor = self.connection.cursor()
        
        # Construire la requête SQL selon les paramètres
        query = """
            SELECT date, opening_price, closing_price, highest_price, lowest_price, volume
            FROM stock_prices
            WHERE stock_id = ?
        """
        params = [stock_id]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date ASC"
        
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def get_latest_price(self, symbol: str) -> Optional[Tuple]:
        """
        Récupère le dernier prix enregistré pour une action
        
        Args:
            symbol (str): Symbole boursier
            
        Returns:
            Tuple: (date, open, close, high, low, volume) ou None
        """
        stock_id = self.get_stock_id(symbol)
        if stock_id is None:
            return None
        
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT date, opening_price, closing_price, highest_price, lowest_price, volume
            FROM stock_prices
            WHERE stock_id = ?
            ORDER BY date DESC
            LIMIT 1
        """, (stock_id,))
        
        return cursor.fetchone()
    
    def get_all_stocks(self) -> List[Tuple]:
        """
        Récupère la liste de toutes les actions dans la BDD
        
        Returns:
            List[Tuple]: Liste de tuples (id, symbol, name)
        """
        cursor = self.connection.cursor()
        cursor.execute("SELECT id, symbol, name FROM stocks ORDER BY symbol")
        return cursor.fetchall()
    
    def close_connection(self):
        """
        Ferme proprement la connexion à la base de données
        """
        if self.connection:
            self.connection.close()
            print("Connexion à la base de données fermée")
    
    def __del__(self):
        """
        Destructeur: ferme la connexion automatiquement
        """
        self.close_connection()