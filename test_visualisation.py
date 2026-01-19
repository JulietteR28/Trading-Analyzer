# -*- coding: utf-8 -*-
"""
Demo Visualisation - Trading Analyzer
Creation de graphiques avec vraies donnees API
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.data_fetcher import DataFetcher
from analysis.statistics import Analyzer
from visualization.charts import ChartGenerator

print("=" * 70)
print("DEMONSTRATION - VISUALISATION")
print("=" * 70)

# Creer le dossier exports s'il n'existe pas
os.makedirs('data/exports', exist_ok=True)

# Initialiser
fetcher = DataFetcher()
chart_gen = ChartGenerator()

# ========== PARTIE 1 : GRAPHIQUE SIMPLE D'UNE ACTION ==========
print("\n[1/4] GRAPHIQUE DE PRIX - APPLE (AAPL)")
print("-" * 70)

print("Recuperation des donnees AAPL (3 mois)...")
hist_aapl = fetcher.fetch_historical_data("AAPL", period="3mo")

if hist_aapl is not None and not hist_aapl.empty:
    print(f"  {len(hist_aapl)} jours de donnees recuperes")
    
    # Creer le graphique
    fig1 = chart_gen.create_price_chart(
        hist_aapl, 
        "Prix de Apple Inc. (AAPL) - 3 derniers mois"
    )
    
    # Sauvegarder
    chart_gen.save_chart(fig1, "aapl_prix.png")
    
    print("\n  Graphique cree: data/exports/aapl_prix.png")
else:
    print("  ERREUR: Impossible de recuperer les donnees")

# ========== PARTIE 2 : GRAPHIQUE AVEC MOYENNE MOBILE ==========
print("\n\n[2/4] GRAPHIQUE AVEC MOYENNE MOBILE - GOOGLE (GOOGL)")
print("-" * 70)

print("Recuperation des donnees GOOGL (3 mois)...")
hist_googl = fetcher.fetch_historical_data("GOOGL", period="3mo")

if hist_googl is not None and not hist_googl.empty:
    print(f"  {len(hist_googl)} jours de donnees recuperes")
    
    # Calculer la moyenne mobile
    analyzer = Analyzer(hist_googl)
    ma_20 = analyzer.calculate_moving_average(window=20)
    
    # Creer le graphique
    fig2 = chart_gen.create_price_with_ma(
        hist_googl,
        ma_20,
        "Prix de Alphabet Inc. (GOOGL) avec Moyenne Mobile",
        window=20
    )
    
    # Sauvegarder
    chart_gen.save_chart(fig2, "googl_prix_ma.png")
    
    print("\n  Graphique cree: data/exports/googl_prix_ma.png")
    print("  La ligne rouge pointillee est la moyenne mobile sur 20 jours")
else:
    print("  ERREUR: Impossible de recuperer les donnees")

# ========== PARTIE 3 : COMPARAISON DE PLUSIEURS ACTIONS ==========
print("\n\n[3/4] COMPARAISON DE PLUSIEURS ACTIONS")
print("-" * 70)

symbols = ["AAPL", "GOOGL", "MSFT"]
print(f"Recuperation de {len(symbols)} actions: {', '.join(symbols)}")
print("(Cela peut prendre quelques secondes...)\n")

stocks_data = {}

for symbol in symbols:
    print(f"  Recuperation de {symbol}...")
    hist = fetcher.fetch_historical_data(symbol, period="3mo")
    
    if hist is not None and not hist.empty:
        stocks_data[symbol] = hist
        print(f"    OK: {len(hist)} jours")
    else:
        print(f"    ERREUR")

if len(stocks_data) > 0:
    print(f"\n{len(stocks_data)} actions recuperees avec succes")
    
    # Creer le graphique de comparaison
    fig3 = chart_gen.create_comparison_chart(
        stocks_data,
        "Comparaison AAPL vs GOOGL vs MSFT (3 mois)"
    )
    
    # Sauvegarder
    chart_gen.save_chart(fig3, "comparaison_tech.png")
    
    print("\n  Graphique cree: data/exports/comparaison_tech.png")
    print("  Les prix sont normalises (base 100) pour comparer les performances")
else:
    print("\n  ERREUR: Aucune action recuperee")

# ========== PARTIE 4 : GRAPHIQUE DES VOLUMES ==========
print("\n\n[4/4] GRAPHIQUE DES VOLUMES - MICROSOFT (MSFT)")
print("-" * 70)

print("Recuperation des donnees MSFT (3 mois)...")
hist_msft = fetcher.fetch_historical_data("MSFT", period="3mo")

if hist_msft is not None and not hist_msft.empty:
    print(f"  {len(hist_msft)} jours de donnees recuperes")
    
    # Creer le graphique
    fig4 = chart_gen.create_volume_chart(
        hist_msft,
        "Volume de transactions - Microsoft Corp. (MSFT)"
    )
    
    # Sauvegarder
    chart_gen.save_chart(fig4, "msft_volume.png")
    
    print("\n  Graphique cree: data/exports/msft_volume.png")
else:
    print("  ERREUR: Impossible de recuperer les donnees")

# Fermer tous les graphiques
chart_gen.close_all()

# ========== RESUME ==========
print("\n\n" + "=" * 70)
print("RESUME")
print("=" * 70)

print("\nGraphiques crees:")
print("  1. data/exports/aapl_prix.png")
print("     -> Prix de AAPL sur 3 mois")
print("\n  2. data/exports/googl_prix_ma.png")
print("     -> Prix de GOOGL avec moyenne mobile (20 jours)")
print("\n  3. data/exports/comparaison_tech.png")
print("     -> Comparaison AAPL vs GOOGL vs MSFT")
print("\n  4. data/exports/msft_volume.png")
print("     -> Volumes de transactions MSFT")

print("\nTypes de graphiques demontres:")
print("  [OK] Graphique de prix simple (ligne)")
print("  [OK] Graphique avec indicateur (moyenne mobile)")
print("  [OK] Graphique de comparaison (plusieurs actions)")
print("  [OK] Graphique de volume (barres)")

print("\nVous pouvez ouvrir les fichiers PNG pour voir les graphiques!")

print("\n" + "=" * 70)
print("DEMONSTRATION TERMINEE")
print("=" * 70)