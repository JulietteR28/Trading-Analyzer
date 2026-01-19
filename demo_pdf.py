# -*- coding: utf-8 -*-
"""
Demo PDF Generator - Trading Analyzer
Generation d'un rapport PDF complet avec donnees et graphiques
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.data_fetcher import DataFetcher
from models.portfolio import Portfolio
from analysis.statistics import Analyzer
from analysis.indicators import TechnicalIndicators
from visualization.charts import ChartGenerator
from reports.pdf_generator import PDFGenerator
from datetime import datetime
from reportlab.lib.units import cm
print("=" * 70)
print("GENERATION DE RAPPORT PDF COMPLET")
print("=" * 70)

# Creer les dossiers necessaires
os.makedirs('data/exports', exist_ok=True)

# ========== ETAPE 1 : RECUPERER LES DONNEES ==========
print("\n[1/4] RECUPERATION DES DONNEES")
print("-" * 70)

fetcher = DataFetcher()
symbols = ["AAPL", "GOOGL", "MSFT"]

print(f"Recuperation de {len(symbols)} actions: {', '.join(symbols)}")
print("(Cela peut prendre quelques secondes...)\n")

stocks = []
stocks_history = {}

for symbol in symbols:
    print(f"  Recuperation de {symbol}...")
    
    # Stock actuel
    stock = fetcher.create_stock_from_api(symbol)
    if stock:
        stocks.append(stock)
        print(f"    Prix: ${stock.current_price:.2f}")
    
    # Historique
    hist = fetcher.fetch_historical_data(symbol, period="3mo")
    if hist is not None and not hist.empty:
        stocks_history[symbol] = hist
        print(f"    Historique: {len(hist)} jours")

print(f"\n  {len(stocks)} actions recuperees avec succes")

# Creer le portfolio
portfolio = Portfolio("Mon Portfolio Tech")
for stock in stocks:
    portfolio.add_stock(stock)

# ========== ETAPE 2 : CREER LES GRAPHIQUES ==========
print("\n\n[2/4] CREATION DES GRAPHIQUES")
print("-" * 70)

chart_gen = ChartGenerator()
graph_files = []

# Graphique 1 : Comparaison
if len(stocks_history) > 0:
    print("  Creation du graphique de comparaison...")
    fig_comp = chart_gen.create_comparison_chart(
        stocks_history,
        "Comparaison des performances (3 mois)"
    )
    chart_gen.save_chart(fig_comp, "rapport_comparaison.png")
    graph_files.append("data/exports/rapport_comparaison.png")
    print("     Graphique sauvegarde")

# Graphiques individuels pour chaque action
for symbol in symbols:
    if symbol in stocks_history:
        hist = stocks_history[symbol]
        
        print(f"  Creation du graphique pour {symbol}...")
        
        # Calculer la moyenne mobile
        analyzer = Analyzer(hist)
        ma = analyzer.calculate_moving_average(20)
        
        # Creer le graphique
        fig = chart_gen.create_price_with_ma(
            hist, ma,
            f"Prix de {symbol} avec Moyenne Mobile (20j)",
            window=20
        )
        
        filename = f"rapport_{symbol.lower()}.png"
        chart_gen.save_chart(fig, filename)
        graph_files.append(f"data/exports/{filename}")
        print(f"     Graphique sauvegarde")

chart_gen.close_all()

print(f"\n  {len(graph_files)} graphiques crees")

# ========== ETAPE 3 : GENERER LE PDF ==========
print("\n\n[3/4] GENERATION DU RAPPORT PDF")
print("-" * 70)

pdf = PDFGenerator("rapport_portfolio.pdf")

# PAGE DE COUVERTURE
pdf.add_title_page(
    "Rapport d'Analyse de Portfolio",
    "Trading Analyzer - Analyse technique et financiere"
)

# SECTION 1 : RESUME DU PORTFOLIO
pdf.add_heading("1. Resume du Portfolio")

pdf.add_text(f"Nom du portfolio: <b>{portfolio.name}</b>")
pdf.add_text(f"Date du rapport: <b>{datetime.now().strftime('%d/%m/%Y %H:%M')}</b>")
pdf.add_text(f"Nombre d'actions: <b>{portfolio.get_stocks_count()}</b>")
pdf.add_text(f"Valeur totale: <b>${portfolio.get_total_value():.2f}</b>")
pdf.add_text(f"Variation moyenne: <b>{portfolio.get_average_variation():+.2f}%</b>")

pdf.add_spacer()

# Tableau des actions
print("  Ajout du tableau des actions...")
table_data = [['Symbole', 'Nom', 'Prix actuel', 'Variation']]

for stock in stocks:
    table_data.append([
        stock.symbol,
        stock.name[:30],  # Limiter la longueur
        f"${stock.current_price:.2f}",
        f"{stock.get_variation():+.2f}%"
    ])

pdf.add_table(table_data, col_widths=[3*cm, 7*cm, 3*cm, 3*cm])

# Meilleure et pire performance
if portfolio.get_stocks_count() > 0:
    best = portfolio.get_best_performer()
    worst = portfolio.get_worst_performer()
    
    pdf.add_spacer()
    pdf.add_text(f"<b>Meilleure performance:</b> {best.symbol} ({best.get_variation():+.2f}%)")
    pdf.add_text(f"<b>Moins bonne performance:</b> {worst.symbol} ({worst.get_variation():+.2f}%)")

# SECTION 2 : GRAPHIQUE DE COMPARAISON
pdf.add_page_break()
pdf.add_heading("2. Comparaison des Performances")

pdf.add_text("Le graphique suivant compare les performances relatives des actions du portfolio sur les 3 derniers mois.")
pdf.add_text("Les prix sont normalises (base 100) pour faciliter la comparaison.")

pdf.add_spacer()

if len(graph_files) > 0:
    print("  Ajout du graphique de comparaison...")
    pdf.add_image(graph_files[0], width=12*cm)

# SECTION 3 : ANALYSE DETAILLEE DE CHAQUE ACTION
pdf.add_page_break()
pdf.add_heading("3. Analyse Detaillee par Action")

for i, symbol in enumerate(symbols):
    if symbol not in stocks_history:
        continue
    
    print(f"  Ajout de l'analyse pour {symbol}...")
    
    # Sous-titre
    stock = next((s for s in stocks if s.symbol == symbol), None)
    if stock:
        pdf.add_text(f"<b>{symbol} - {stock.name}</b>", )
    
    pdf.add_spacer(0.3*cm)
    
    # Analyse
    hist = stocks_history[symbol]
    analyzer = Analyzer(hist)
    indicators = TechnicalIndicators(hist)
    
    # Statistiques
    stats = analyzer.get_statistics()
    pdf.add_text(f"Prix moyen (3 mois): ${stats['prix_moyen']:.2f}")
    pdf.add_text(f"Prix minimum: ${stats['prix_min']:.2f}")
    pdf.add_text(f"Prix maximum: ${stats['prix_max']:.2f}")
    
    vol = analyzer.calculate_volatility()
    if vol:
        pdf.add_text(f"Volatilite: {vol:.2f}%")
    
    trend = analyzer.calculate_trend()
    pdf.add_text(f"Tendance: {trend}")
    
    # RSI
    rsi = indicators.calculate_rsi()
    if rsi:
        pdf.add_text(f"RSI (14 jours): {rsi:.2f}")
        if rsi < 30:
            pdf.add_text("  -> Survendu (opportunite d'achat potentielle)")
        elif rsi > 70:
            pdf.add_text("  -> Surachete (attention a la surcote)")
        else:
            pdf.add_text("  -> Zone normale")
    
    # Signal
    signal = indicators.get_simple_signal()
    pdf.add_text(f"<b>Signal de trading: {signal}</b>")
    
    pdf.add_spacer()
    
    # Graphique
    if i + 1 < len(graph_files):
        pdf.add_image(graph_files[i + 1], width=12*cm)
    
    if i < len(symbols) - 1:
        pdf.add_page_break()

# SECTION 4 : CONCLUSION
pdf.add_page_break()
pdf.add_heading("4. Conclusion")

pdf.add_text("Ce rapport presente une analyse complete du portfolio base sur:")
pdf.add_text("- Les donnees de marche en temps reel")
pdf.add_text("- Des indicateurs techniques (RSI, moyennes mobiles)")
pdf.add_text("- L'analyse statistique (volatilite, tendances)")

pdf.add_spacer()

if portfolio.get_average_variation() > 0:
    pdf.add_text(f"<b>Le portfolio presente une performance positive avec une variation moyenne de {portfolio.get_average_variation():+.2f}%.</b>")
else:
    pdf.add_text(f"<b>Le portfolio presente une performance negative avec une variation moyenne de {portfolio.get_average_variation():+.2f}%.</b>")

pdf.add_spacer()
pdf.add_text("Note: Ce rapport est genere automatiquement par Trading Analyzer.")
pdf.add_text("Les donnees sont fournies a titre informatif uniquement.")

# ========== ETAPE 4 : GENERER LE PDF FINAL ==========
print("\n\n[4/4] FINALISATION")
print("-" * 70)

filepath = pdf.generate()

# ========== RESUME ==========
print("\n\n" + "=" * 70)
print("RAPPORT PDF GENERE AVEC SUCCES")
print("=" * 70)

print(f"\nFichier: {filepath}")
print(f"Taille: ~{os.path.getsize(filepath) / 1024:.0f} KB")

print("\nContenu du rapport:")
print("  - Page de couverture")
print(f"  - Resume du portfolio ({len(stocks)} actions)")
print(f"  - Graphique de comparaison")
print(f"  - Analyse detaillee de {len(symbols)} actions")
print(f"  - {len(graph_files)} graphiques inclus")
print("  - Conclusion")

print("\nVous pouvez ouvrir le fichier PDF pour voir le rapport complet!")

print("\n" + "=" * 70)