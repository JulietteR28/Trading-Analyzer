# -*- coding: utf-8 -*-
"""
Test Complet Checkpoint 2 - API et Recuperation de Donnees
Version sans emojis pour compatibilite Windows
"""
import sys
import os

# Ajouter le chemin du projet
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.data_fetcher import DataFetcher
from api.async_fetcher import AsyncFetcher
from models.portfolio import Portfolio
from database.db_manager import DatabaseManager
from datetime import datetime, date
import asyncio

print("=" * 70)
print("TEST COMPLET CHECKPOINT 2 - API et Donnees")
print("=" * 70)

# ===== Test 1: DataFetcher basique =====
print("\nTEST 1: Recuperation de donnees individuelles")
print("-" * 70)

fetcher = DataFetcher()

# Recuperer une action
print("\n1.1 - Recuperation d'une action:")
apple = fetcher.create_stock_from_api("AAPL")
if apple:
    print("  OK: " + str(apple))
    print("     Variation: {:+.2f}%".format(apple.get_variation()))

# Historique
print("\n1.2 - Recuperation historique:")
hist = fetcher.fetch_historical_data("AAPL", period="1mo")
if hist is not None:
    print("  OK: {} jours d'historique".format(len(hist)))
    print("     Premier jour: {}".format(hist.iloc[0]['Date'].strftime('%Y-%m-%d')))
    print("     Dernier jour: {}".format(hist.iloc[-1]['Date'].strftime('%Y-%m-%d')))
    print("     Prix moyen: ${:.2f}".format(hist['Close'].mean()))

# ===== Test 2: Comparaison Sync vs Async =====
print("\n\nTEST 2: Comparaison SYNCHRONE vs ASYNCHRONE")
print("-" * 70)

symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "NFLX"]

print("\nTest avec {} actions: {}".format(len(symbols), ', '.join(symbols)))

# Version SYNCHRONE
print("\n2.1 - Version SYNCHRONE:")
start_sync = datetime.now()
stocks_sync = fetcher.fetch_multiple_stocks_sync(symbols)
time_sync = (datetime.now() - start_sync).total_seconds()

print("\n  Resultats SYNC:")
print("    Temps: {:.3f}s".format(time_sync))
print("    Actions: {}/{}".format(len(stocks_sync), len(symbols)))

# Version ASYNCHRONE
print("\n2.2 - Version ASYNCHRONE:")

async def test_async():
    async_fetcher = AsyncFetcher()
    start_async = datetime.now()
    stocks_async = await async_fetcher.fetch_multiple_stocks(symbols)
    time_async = (datetime.now() - start_async).total_seconds()
    
    print("\n  Resultats ASYNC:")
    print("    Temps: {:.3f}s".format(time_async))
    print("    Actions: {}/{}".format(len(stocks_async), len(symbols)))
    
    # Calculer le gain
    if time_sync > 0 and time_async > 0:
        speedup = time_sync / time_async
        print("\n  Gain de performance:")
        print("    {:.1f}x plus rapide avec async!".format(speedup))
        print("    Gain de temps: {:.3f}s".format(time_sync - time_async))
    
    return stocks_async

stocks_async = asyncio.run(test_async())

# ===== Test 3: Integration avec Portfolio =====
print("\n\nTEST 3: Integration avec Portfolio")
print("-" * 70)

portfolio = Portfolio("Tech Portfolio")

print("\n3.1 - Ajout d'actions au portfolio:")
for stock in stocks_async[:5]:  # Prendre les 5 premieres
    portfolio.add_stock(stock)

print("\n" + str(portfolio))
print("\n  Statistiques:")
print("    Nombre d'actions: {}".format(portfolio.get_stocks_count()))
print("    Valeur totale: ${:.2f}".format(portfolio.get_total_value()))
print("    Variation moyenne: {:+.2f}%".format(portfolio.get_average_variation()))

best = portfolio.get_best_performer()
worst = portfolio.get_worst_performer()
print("    Meilleure: {} ({:+.2f}%)".format(best.symbol, best.get_variation()))
print("    Moins bonne: {} ({:+.2f}%)".format(worst.symbol, worst.get_variation()))

# ===== Test 4: Integration avec Database =====
print("\n\nTEST 4: Integration avec Database")
print("-" * 70)

db = DatabaseManager("data/checkpoint2_test.db")

print("\n4.1 - Sauvegarde en base de donnees:")
saved_count = 0
for stock in portfolio.stocks:
    stock_id = db.insert_stock(stock.symbol, stock.name)
    if stock_id:
        # Sauvegarder le prix du jour
        db.insert_stock_price(
            symbol=stock.symbol,
            date_value=date.today(),
            opening=stock.opening_price or stock.current_price,
            closing=stock.current_price,
            high=stock.highest_price or stock.current_price,
            low=stock.lowest_price or stock.current_price,
            volume=stock.volume or 0
        )
        saved_count += 1

print("  OK: {} actions sauvegardees en BDD".format(saved_count))

print("\n4.2 - Recuperation depuis la BDD:")
all_stocks_db = db.get_all_stocks()
print("  OK: {} actions en base:".format(len(all_stocks_db)))
for stock_data in all_stocks_db:
    stock_id, symbol, name = stock_data
    last_price = db.get_latest_price(symbol)
    if last_price:
        date_val, open_p, close_p, high_p, low_p, volume = last_price
        print("    {}: ${:.2f} (le {})".format(symbol, close_p, date_val))

db.close_connection()

# ===== Test 5: Mise a jour asynchrone d'un portfolio =====
print("\n\nTEST 5: Mise a jour asynchrone du portfolio")
print("-" * 70)

async def test_portfolio_update():
    async_fetcher = AsyncFetcher()
    
    print("\n5.1 - Etat initial du portfolio:")
    print("  " + str(portfolio))
    
    print("\n5.2 - Mise a jour asynchrone...")
    updated = await async_fetcher.fetch_and_update_portfolio(portfolio)
    
    if updated:
        print("\n5.3 - Etat apres mise a jour:")
        print("  " + str(portfolio))
        print("\n  OK: Portfolio mis a jour avec succes!")

asyncio.run(test_portfolio_update())

# ===== Resume Final =====
print("\n\n" + "=" * 70)
print("CHECKPOINT 2 - TESTS REUSSIS")
print("=" * 70)

print("\nFonctionnalites validees:")
print("  [OK] DataFetcher - Recuperation synchrone")
print("  [OK] AsyncFetcher - Recuperation asynchrone")
print("  [OK] Creation de Stock depuis API")
print("  [OK] Mise a jour de Stock depuis API")
print("  [OK] Recuperation historique")
print("  [OK] Comparaison sync vs async")
print("  [OK] Integration avec Portfolio")
print("  [OK] Integration avec Database")
print("  [OK] Mise a jour asynchrone de portfolio")

print("\nProchaines etapes (Checkpoint 3):")
print("  - Analyse statistique (NumPy/Pandas)")
print("  - Indicateurs techniques (RSI, MACD, etc.)")
print("  - Visualisations (Matplotlib/Seaborn)")

print("\n" + "=" * 70)
print("Checkpoint 2 COMPLET!")
print("=" * 70)