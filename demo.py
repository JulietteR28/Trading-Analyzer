# -*- coding: utf-8 -*-
"""
Demo Complete - Trading Analyzer
Relie toutes les parties du projet avec vraies donnees API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.data_fetcher import DataFetcher
from models.stock import Stock
from models.portfolio import Portfolio
from models.transaction import Transaction, TransactionType
from database.db_manager import DatabaseManager
from analysis.statistics import Analyzer
from analysis.indicators import TechnicalIndicators
from datetime import date

print("=" * 70)
print("TRADING ANALYZER - DEMONSTRATION COMPLETE")
print("=" * 70)

# ========== PARTIE 1 : RECUPERATION DES DONNEES ==========
print("\n[1/5] RECUPERATION DES DONNEES REELLES")
print("-" * 70)

fetcher = DataFetcher()

# Liste d'actions a analyser
symbols = ["AAPL", "GOOGL", "MSFT"]
print(f"\nActions selectionnees: {', '.join(symbols)}")
print("(Cela peut prendre quelques secondes...)\n")

# Recuperer les actions
stocks = []
for symbol in symbols:
    print(f"  Recuperation de {symbol}...")
    stock = fetcher.create_stock_from_api(symbol)
    if stock:
        stocks.append(stock)
        print(f"    OK: {stock}")
    else:
        print(f"    ERREUR: Impossible de recuperer {symbol}")

print(f"\n  {len(stocks)} actions recuperees avec succes!")

# ========== PARTIE 2 : CREATION DU PORTFOLIO ==========
print("\n\n[2/5] CREATION DU PORTFOLIO")
print("-" * 70)

portfolio = Portfolio("Mon Portfolio Tech")

# Ajouter les actions au portfolio
for stock in stocks:
    portfolio.add_stock(stock)

print(f"\n{portfolio}\n")

# Afficher statistiques du portfolio
print("Statistiques du portfolio:")
print(f"  Nombre d'actions: {portfolio.get_stocks_count()}")
print(f"  Valeur totale: ${portfolio.get_total_value():.2f}")
print(f"  Variation moyenne: {portfolio.get_average_variation():+.2f}%")

if portfolio.get_stocks_count() > 0:
    best = portfolio.get_best_performer()
    worst = portfolio.get_worst_performer()
    print(f"  Meilleure performance: {best.symbol} ({best.get_variation():+.2f}%)")
    print(f"  Moins bonne performance: {worst.symbol} ({worst.get_variation():+.2f}%)")

# ========== PARTIE 3 : ANALYSE DETAILLEE DE CHAQUE ACTION ==========
print("\n\n[3/5] ANALYSE DETAILLEE DE CHAQUE ACTION")
print("-" * 70)

for stock in stocks:
    print(f"\n--- Analyse de {stock.symbol} ({stock.name}) ---")
    
    # Recuperer l'historique
    print(f"  Recuperation de l'historique (3 mois)...")
    hist = fetcher.fetch_historical_data(stock.symbol, period="3mo")
    
    if hist is not None and not hist.empty:
        # Analyse statistique
        analyzer = Analyzer(hist)
        
        print("\n  Statistiques:")
        stats = analyzer.get_statistics()
        print(f"    Prix moyen (3 mois): ${stats['prix_moyen']:.2f}")
        print(f"    Prix min: ${stats['prix_min']:.2f}")
        print(f"    Prix max: ${stats['prix_max']:.2f}")
        
        # Moyenne mobile
        ma = analyzer.calculate_moving_average(window=20)
        if ma is not None and not ma.empty:
            print(f"    Moyenne mobile (20j): ${ma.iloc[-1]:.2f}")
        
        # Volatilite
        vol = analyzer.calculate_volatility()
        if vol is not None:
            print(f"    Volatilite: {vol:.2f}%")
        
        # Tendance
        trend = analyzer.calculate_trend()
        emoji = "📈" if trend == "HAUSSE" else "📉" if trend == "BAISSE" else "➡️"
        print(f"    Tendance: {emoji} {trend}")
        
        # Indicateurs techniques
        indicators = TechnicalIndicators(hist)
        
        print("\n  Indicateurs techniques:")
        rsi = indicators.calculate_rsi()
        if rsi is not None:
            print(f"    RSI (14j): {rsi:.2f}")
            if rsi < 30:
                print(f"      -> Survendu (peut-etre une bonne affaire)")
            elif rsi > 70:
                print(f"      -> Surachete (peut-etre trop cher)")
            else:
                print(f"      -> Zone normale")
        
        # Signal de trading
        print("\n  Signal de trading:")
        signal = indicators.get_simple_signal()
        if signal == "ACHETER":
            print(f"    🟢 {signal} - Opportunite d'achat potentielle")
        elif signal == "VENDRE":
            print(f"    🔴 {signal} - Envisager une vente")
        else:
            print(f"    ⏸️  {signal} - Rester en observation")
        
        # Variation de prix
        change = indicators.calculate_price_change()
        print(f"\n  Evolution sur 3 mois:")
        print(f"    Prix debut: ${change['prix_debut']:.2f}")
        print(f"    Prix actuel: ${change['prix_fin']:.2f}")
        print(f"    Variation: {change['variation_pct']:+.2f}%")
    else:
        print("  ERREUR: Impossible de recuperer l'historique")

# ========== PARTIE 4 : SAUVEGARDE EN BASE DE DONNEES ==========
print("\n\n[4/5] SAUVEGARDE EN BASE DE DONNEES")
print("-" * 70)

db = DatabaseManager("data/trading_analyzer.db")

print("\nSauvegarde des actions et des prix...")
for stock in stocks:
    # Sauvegarder l'action
    stock_id = db.insert_stock(stock.symbol, stock.name)
    
    # Sauvegarder le prix du jour
    if stock_id:
        db.insert_stock_price(
            symbol=stock.symbol,
            date_value=date.today(),
            opening=stock.opening_price or stock.current_price,
            closing=stock.current_price,
            high=stock.highest_price or stock.current_price,
            low=stock.lowest_price or stock.current_price,
            volume=stock.volume or 0
        )

print(f"  OK: {len(stocks)} actions sauvegardees")

# Afficher le contenu de la base
print("\nContenu de la base de donnees:")
all_stocks_db = db.get_all_stocks()
for stock_data in all_stocks_db:
    stock_id, symbol, name = stock_data
    last_price = db.get_latest_price(symbol)
    if last_price:
        date_val, open_p, close_p, high_p, low_p, volume = last_price
        print(f"  {symbol}: ${close_p:.2f} (enregistre le {date_val})")

db.close_connection()

# ========== PARTIE 5 : SIMULATION DE TRANSACTIONS ==========
print("\n\n[5/5] SIMULATION DE TRANSACTIONS")
print("-" * 70)

print("\nExemple de transactions:")

# Simuler quelques transactions
transactions = []

if len(stocks) > 0:
    # Achat 1
    trans1 = Transaction(
        stock_symbol=stocks[0].symbol,
        transaction_type=TransactionType.BUY,
        quantity=10,
        price_per_share=stocks[0].current_price,
        fees=5.0
    )
    transactions.append(trans1)
    print(f"  {trans1}")

if len(stocks) > 1:
    # Achat 2
    trans2 = Transaction(
        stock_symbol=stocks[1].symbol,
        transaction_type=TransactionType.BUY,
        quantity=5,
        price_per_share=stocks[1].current_price,
        fees=5.0
    )
    transactions.append(trans2)
    print(f"  {trans2}")

# Calcul du total investi
total_invested = sum(t.get_total_amount() for t in transactions if t.is_buy())
print(f"\nTotal investi: ${total_invested:.2f}")

# ========== RESUME FINAL ==========
print("\n\n" + "=" * 70)
print("RESUME DE LA DEMONSTRATION")
print("=" * 70)

print(f"\nActions analysees: {len(stocks)}")
for stock in stocks:
    variation_emoji = "🟢" if stock.get_variation() > 0 else "🔴"
    print(f"  {variation_emoji} {stock.symbol}: ${stock.current_price:.2f} ({stock.get_variation():+.2f}%)")

print(f"\nPortfolio:")
print(f"  Nom: {portfolio.name}")
print(f"  Valeur totale: ${portfolio.get_total_value():.2f}")
print(f"  Variation moyenne: {portfolio.get_average_variation():+.2f}%")

print(f"\nTransactions:")
print(f"  Nombre: {len(transactions)}")
print(f"  Montant total: ${total_invested:.2f}")

print(f"\nBase de donnees:")
print(f"  Fichier: data/trading_analyzer.db")
print(f"  Actions enregistrees: {len(all_stocks_db)}")

print("\n" + "=" * 70)
print("DEMONSTRATION TERMINEE AVEC SUCCES!")
print("=" * 70)

print("\nFonctionnalites demontrees:")
print("  [OK] Recuperation de donnees reelles via API")
print("  [OK] Creation et gestion de portfolio")
print("  [OK] Analyse statistique (moyennes, volatilite)")
print("  [OK] Indicateurs techniques (RSI, signaux)")
print("  [OK] Sauvegarde en base de donnees SQLite")
print("  [OK] Gestion de transactions")

print("\nProchaines etapes:")
print("  - Visualisations (graphiques)")
print("  - Generation de rapports PDF")
print("  - Interface graphique simple")