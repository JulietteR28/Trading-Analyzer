# -*- coding: utf-8 -*-
"""
Trading Analyzer - Application principale
Point d'entree du programme
"""
import sys
import os

# Ajouter le repertoire courant au path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.data_fetcher import DataFetcher
from models.stock import Stock
from models.portfolio import Portfolio
from database.db_manager import DatabaseManager
from analysis.statistics import Analyzer
from analysis.indicators import TechnicalIndicators
from visualization.charts import ChartGenerator
from reports.pdf_generator import PDFGenerator
from datetime import datetime, date
from reportlab.lib.units import cm


def afficher_menu():
    """Affiche le menu principal"""
    print("\n" + "=" * 70)
    print("TRADING ANALYZER - Menu Principal")
    print("=" * 70)
    print("\n1. Analyser une action en temps reel (avec API)")
    print("2. Voir les actions en base de donnees")
    print("3. Creer un portfolio avec donnees reelles")
    print("4. Creer des visualisations (graphiques)")
    print("5. Generer un rapport PDF avec actions du portfolio")
    print("0. Quitter")
    print("=" * 70)


def analyser_action():
    """Analyse une action en temps reel avec l'API"""
    print("\n" + "=" * 70)
    print("ANALYSE D'ACTION EN TEMPS REEL")
    print("=" * 70)
    
    symbol = input("\nEntrez le symbole de l'action (ex: AAPL, GOOGL, MSFT): ").upper().strip()
    
    if not symbol:
        print("Erreur: Symbole invalide")
        return
    
    print(f"\nRecuperation des donnees pour {symbol}...")
    
    try:
        # Initialiser le fetcher
        fetcher = DataFetcher()
        
        # Recuperer le stock
        stock = fetcher.create_stock_from_api(symbol)
        
        if not stock:
            print(f"Erreur: Action '{symbol}' introuvable")
            return
        
        # Afficher les infos de base
        print("\n" + "-" * 70)
        print(f"{stock.name} ({stock.symbol})")
        print("-" * 70)
        print(f"Prix actuel: ${stock.current_price:.2f}")
        print(f"Variation: {stock.get_variation():+.2f}%")
        
        if stock.highest_price:
            print(f"Plus haut du jour: ${stock.highest_price:.2f}")
        if stock.lowest_price:
            print(f"Plus bas du jour: ${stock.lowest_price:.2f}")
        if stock.volume:
            print(f"Volume: {stock.volume:,}")
        
        # Recuperer l'historique
        print(f"\nRecuperation de l'historique (3 mois)...")
        hist = fetcher.fetch_historical_data(symbol, period="3mo")
        
        if hist is not None and not hist.empty:
            print(f"OK: {len(hist)} jours d'historique recuperes")
            
            # Analyse statistique
            analyzer = Analyzer(hist)
            stats = analyzer.get_statistics()
            
            print("\nSTATISTIQUES (3 mois):")
            print(f"  Prix moyen: ${stats['prix_moyen']:.2f}")
            print(f"  Prix minimum: ${stats['prix_min']:.2f}")
            print(f"  Prix maximum: ${stats['prix_max']:.2f}")
            
            vol = analyzer.calculate_volatility()
            if vol:
                print(f"  Volatilite: {vol:.2f}%")
            
            trend = analyzer.calculate_trend()
            print(f"  Tendance: {trend}")
            
            # Indicateurs techniques
            indicators = TechnicalIndicators(hist)
            
            print("\nINDICATEURS TECHNIQUES:")
            rsi = indicators.calculate_rsi()
            if rsi:
                print(f"  RSI (14 jours): {rsi:.2f}")
                if rsi < 30:
                    print(f"    => Survendu (opportunite d'achat potentielle)")
                elif rsi > 70:
                    print(f"    => Surachete (attention a la surcote)")
                else:
                    print(f"    => Zone normale")
            
            signal = indicators.get_simple_signal()
            print(f"\n  Signal de trading: {signal}")
            
            # Proposer de sauvegarder en BDD
            save = input("\nSauvegarder cette action en base de donnees ? (o/n): ").lower()
            if save == 'o':
                db = DatabaseManager()
                stock_id = db.insert_stock(stock.symbol, stock.name)
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
                    print("Action sauvegardee en base de donnees")
                db.close_connection()
        
        else:
            print("Attention: Impossible de recuperer l'historique")
    
    except Exception as e:
        print(f"Erreur lors de l'analyse: {e}")


def afficher_actions_bdd():
    """Affiche toutes les actions en base de donnees"""
    print("\n" + "=" * 70)
    print("ACTIONS EN BASE DE DONNEES")
    print("=" * 70)
    
    try:
        db = DatabaseManager()
        actions = db.get_all_stocks()
        
        if not actions:
            print("\nAucune action en base de donnees.")
            print("Conseil: Utilisez l'option 1 pour analyser et sauvegarder des actions")
        else:
            print(f"\n{len(actions)} action(s) trouvee(s):\n")
            for stock_data in actions:
                stock_id, symbol, name = stock_data
                print(f"  [{stock_id}] {symbol} - {name}")
                
                # Recuperer le dernier prix
                last_price = db.get_latest_price(symbol)
                if last_price:
                    date_val, open_p, close_p, high_p, low_p, volume = last_price
                    variation = ((close_p - open_p) / open_p * 100) if open_p > 0 else 0
                    print(f"      Prix: ${close_p:.2f} ({variation:+.2f}%) - {date_val}")
        
        db.close_connection()
        
    except Exception as e:
        print(f"Erreur: {e}")


def creer_portfolio_reel():
    """Cree un portfolio avec donnees reelles de l'API"""
    print("\n" + "=" * 70)
    print("CREATION DE PORTFOLIO AVEC DONNEES REELLES")
    print("=" * 70)
    
    nom = input("\nNom du portfolio (ex: 'Tech Stocks'): ").strip()
    if not nom:
        nom = "Mon Portfolio"
    
    portfolio = Portfolio(nom)
    
    print(f"\nPortfolio '{nom}' cree")
    print("\nEntrez les symboles des actions a ajouter (un par ligne)")
    print("Exemples: AAPL, GOOGL, MSFT, TSLA, AMZN")
    print("Tapez 'fin' pour terminer\n")
    
    fetcher = DataFetcher()
    
    while True:
        symbol = input("Symbole (ou 'fin'): ").upper().strip()
        
        if symbol == 'FIN' or symbol == '':
            break
        
        print(f"Recuperation de {symbol}...")
        
        try:
            stock = fetcher.create_stock_from_api(symbol)
            
            if stock:
                portfolio.add_stock(stock)
                print(f"OK: {stock.name}: ${stock.current_price:.2f} ({stock.get_variation():+.2f}%)")
            else:
                print(f"Erreur: Action '{symbol}' introuvable")
        
        except Exception as e:
            print(f"Erreur: {e}")
    
    # Afficher le resume
    if portfolio.get_stocks_count() > 0:
        print("\n" + "-" * 70)
        print(f"RESUME DU PORTFOLIO '{portfolio.name}'")
        print("-" * 70)
        print(f"Nombre d'actions: {portfolio.get_stocks_count()}")
        print(f"Valeur totale: ${portfolio.get_total_value():.2f}")
        
        avg_var = portfolio.get_average_variation()
        if avg_var:
            print(f"Variation moyenne: {avg_var:+.2f}%")
        
        best = portfolio.get_best_performer()
        worst = portfolio.get_worst_performer()
        
        if best:
            print(f"\nMeilleure performance: {best.symbol} ({best.get_variation():+.2f}%)")
        if worst:
            print(f"Moins bonne performance: {worst.symbol} ({worst.get_variation():+.2f}%)")
        
        # Sauvegarder le portfolio pour utilisation ulterieure
        global current_portfolio
        current_portfolio = portfolio
        print("\nPortfolio sauvegarde en memoire pour les options 4 et 5")
    else:
        print("\nPortfolio vide")


def creer_visualisations():
    """Cree des graphiques pour les actions"""
    print("\n" + "=" * 70)
    print("CREATION DE VISUALISATIONS")
    print("=" * 70)
    
    # Verifier si un portfolio existe
    if 'current_portfolio' not in globals() or current_portfolio is None:
        print("\nAucun portfolio en memoire.")
        print("Conseil: Utilisez d'abord l'option 3 pour creer un portfolio")
        return
    
    portfolio = current_portfolio
    
    if portfolio.get_stocks_count() == 0:
        print("\nLe portfolio est vide.")
        return
    
    print(f"\nPortfolio: {portfolio.name}")
    print(f"Actions: {portfolio.get_stocks_count()}")
    
    # Demander quel type de graphique
    print("\nTypes de graphiques disponibles:")
    print("1. Graphique de prix pour une action")
    print("2. Graphique avec moyenne mobile")
    print("3. Comparaison de plusieurs actions")
    print("4. Tous les graphiques")
    
    choix = input("\nVotre choix (1-4): ").strip()
    
    try:
        fetcher = DataFetcher()
        chart_gen = ChartGenerator()
        os.makedirs('data/exports', exist_ok=True)
        
        if choix == '1':
            # Graphique simple pour une action
            symbol = input("\nSymbole de l'action: ").upper().strip()
            stock = portfolio.get_stock(symbol)
            
            if not stock:
                print(f"Erreur: {symbol} n'est pas dans le portfolio")
                return
            
            print(f"Recuperation de l'historique pour {symbol}...")
            hist = fetcher.fetch_historical_data(symbol, period="3mo")
            
            if hist is not None and not hist.empty:
                fig = chart_gen.create_price_chart(hist, f"Prix de {stock.name}")
                chart_gen.save_chart(fig, f"{symbol}_prix.png")
                print(f"\nGraphique sauvegarde: data/exports/{symbol}_prix.png")
            else:
                print("Erreur: Impossible de recuperer l'historique")
        
        elif choix == '2':
            # Graphique avec moyenne mobile
            symbol = input("\nSymbole de l'action: ").upper().strip()
            stock = portfolio.get_stock(symbol)
            
            if not stock:
                print(f"Erreur: {symbol} n'est pas dans le portfolio")
                return
            
            print(f"Recuperation de l'historique pour {symbol}...")
            hist = fetcher.fetch_historical_data(symbol, period="3mo")
            
            if hist is not None and not hist.empty:
                analyzer = Analyzer(hist)
                ma = analyzer.calculate_moving_average(20)
                
                fig = chart_gen.create_price_with_ma(
                    hist, ma, 
                    f"Prix de {stock.name} avec Moyenne Mobile",
                    window=20
                )
                chart_gen.save_chart(fig, f"{symbol}_prix_ma.png")
                print(f"\nGraphique sauvegarde: data/exports/{symbol}_prix_ma.png")
            else:
                print("Erreur: Impossible de recuperer l'historique")
        
        elif choix == '3':
            # Comparaison de plusieurs actions
            print("\nRecuperation de l'historique pour toutes les actions...")
            stocks_data = {}
            
            for stock in portfolio.stocks:
                hist = fetcher.fetch_historical_data(stock.symbol, period="3mo")
                if hist is not None and not hist.empty:
                    stocks_data[stock.symbol] = hist
                    print(f"  OK: {stock.symbol}")
            
            if len(stocks_data) > 0:
                fig = chart_gen.create_comparison_chart(
                    stocks_data,
                    f"Comparaison du portfolio {portfolio.name}"
                )
                chart_gen.save_chart(fig, "comparaison_portfolio.png")
                print(f"\nGraphique sauvegarde: data/exports/comparaison_portfolio.png")
            else:
                print("Erreur: Aucune donnee recuperee")
        
        elif choix == '4':
            # Tous les graphiques
            print("\nCreation de tous les graphiques...")
            
            # 1. Comparaison
            print("\n1. Graphique de comparaison...")
            stocks_data = {}
            for stock in portfolio.stocks:
                hist = fetcher.fetch_historical_data(stock.symbol, period="3mo")
                if hist is not None and not hist.empty:
                    stocks_data[stock.symbol] = hist
            
            if len(stocks_data) > 0:
                fig = chart_gen.create_comparison_chart(
                    stocks_data,
                    f"Comparaison du portfolio {portfolio.name}"
                )
                chart_gen.save_chart(fig, "comparaison_portfolio.png")
                print("   Sauvegarde: data/exports/comparaison_portfolio.png")
            
            # 2. Graphiques individuels avec MA
            print("\n2. Graphiques individuels avec moyenne mobile...")
            for stock in portfolio.stocks:
                hist = fetcher.fetch_historical_data(stock.symbol, period="3mo")
                if hist is not None and not hist.empty:
                    analyzer = Analyzer(hist)
                    ma = analyzer.calculate_moving_average(20)
                    
                    fig = chart_gen.create_price_with_ma(
                        hist, ma,
                        f"Prix de {stock.name} avec MA(20)",
                        window=20
                    )
                    chart_gen.save_chart(fig, f"{stock.symbol}_prix_ma.png")
                    print(f"   Sauvegarde: data/exports/{stock.symbol}_prix_ma.png")
            
            print("\nTous les graphiques ont ete crees avec succes!")
        
        else:
            print("Choix invalide")
        
        chart_gen.close_all()
        
    except Exception as e:
        print(f"Erreur lors de la creation des graphiques: {e}")
        import traceback
        traceback.print_exc()


def generer_rapport_pdf():
    """Genere un rapport PDF avec les actions du portfolio"""
    print("\n" + "=" * 70)
    print("GENERATION DE RAPPORT PDF")
    print("=" * 70)
    
    # Verifier si un portfolio existe
    if 'current_portfolio' not in globals() or current_portfolio is None:
        print("\nAucun portfolio en memoire.")
        print("Conseil: Utilisez d'abord l'option 3 pour creer un portfolio")
        return
    
    portfolio = current_portfolio
    
    if portfolio.get_stocks_count() == 0:
        print("\nLe portfolio est vide.")
        return
    
    print(f"\nPortfolio: {portfolio.name}")
    print(f"Actions: {portfolio.get_stocks_count()}")
    
    print("\nGeneration du rapport PDF en cours...")
    print("Cela peut prendre 30-60 secondes...")
    
    try:
        os.makedirs('data/exports', exist_ok=True)
        
        fetcher = DataFetcher()
        chart_gen = ChartGenerator()
        
        # 1. Recuperer les donnees
        print("\n[1/3] Recuperation des donnees...")
        stocks_history = {}
        
        for stock in portfolio.stocks:
            print(f"  Recuperation de {stock.symbol}...")
            hist = fetcher.fetch_historical_data(stock.symbol, period="3mo")
            if hist is not None and not hist.empty:
                stocks_history[stock.symbol] = hist
        
        print(f"  OK: {len(stocks_history)} actions recuperees")
        
        # 2. Creer les graphiques
        print("\n[2/3] Creation des graphiques...")
        graph_files = []
        
        # Graphique de comparaison
        if len(stocks_history) > 1:
            print("  Creation graphique de comparaison...")
            fig = chart_gen.create_comparison_chart(
                stocks_history,
                "Comparaison des performances (3 mois)"
            )
            chart_gen.save_chart(fig, "rapport_comparaison.png")
            graph_files.append("data/exports/rapport_comparaison.png")
        
        # Graphiques individuels
        for symbol in stocks_history.keys():
            print(f"  Creation graphique pour {symbol}...")
            hist = stocks_history[symbol]
            analyzer = Analyzer(hist)
            ma = analyzer.calculate_moving_average(20)
            
            fig = chart_gen.create_price_with_ma(
                hist, ma,
                f"Prix de {symbol} avec Moyenne Mobile (20j)",
                window=20
            )
            filename = f"rapport_{symbol.lower()}.png"
            chart_gen.save_chart(fig, filename)
            graph_files.append(f"data/exports/{filename}")
        
        chart_gen.close_all()
        print(f"  OK: {len(graph_files)} graphiques crees")
        
        # 3. Generer le PDF
        print("\n[3/3] Generation du PDF...")
        pdf = PDFGenerator("rapport_portfolio.pdf")
        
        # Page de couverture
        pdf.add_title_page(
            "Rapport d'Analyse de Portfolio",
            "Trading Analyzer - Analyse technique et financiere"
        )
        
        # Section 1: Resume
        pdf.add_heading("1. Resume du Portfolio")
        pdf.add_text(f"Nom du portfolio: {portfolio.name}")
        pdf.add_text(f"Date du rapport: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        pdf.add_text(f"Nombre d'actions: {portfolio.get_stocks_count()}")
        
        pdf.add_spacer()
        
        # Tableau des actions
        table_data = [['Symbole', 'Nom', 'Prix actuel', 'Variation']]
        for stock in portfolio.stocks:
            table_data.append([
                stock.symbol,
                stock.name[:30],
                f"${stock.current_price:.2f}",
                f"{stock.get_variation():+.2f}%"
            ])
        
        pdf.add_table(table_data, col_widths=[3*cm, 7*cm, 3*cm, 3*cm])
        
        # Section 2: Comparaison
        if len(graph_files) > 0 and len(stocks_history) > 1:
            pdf.add_page_break()
            pdf.add_heading("2. Comparaison des Performances")
            pdf.add_text("Les prix sont normalises (base 100) pour faciliter la comparaison.")
            pdf.add_spacer()
            pdf.add_image(graph_files[0], width=10*cm, height=7*cm)
        
        # Section 3: Analyses detaillees
        pdf.add_page_break()
        pdf.add_heading("3. Analyse Detaillee par Action")
        
        for i, symbol in enumerate(stocks_history.keys()):
            stock = portfolio.get_stock(symbol)
            
            if stock:
                pdf.add_text(f"{symbol} - {stock.name}")
            
            pdf.add_spacer(0.3*cm)
            
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
            
            rsi = indicators.calculate_rsi()
            if rsi:
                pdf.add_text(f"RSI (14 jours): {rsi:.2f}")
            
            signal = indicators.get_simple_signal()
            pdf.add_text(f"Signal de trading: {signal}")
            
            pdf.add_spacer()
            
            # Graphique
            graph_index = i + (1 if len(stocks_history) > 1 else 0)
            if graph_index < len(graph_files):
                pdf.add_image(graph_files[graph_index], width=10*cm, height=7*cm)
            
            if i < len(stocks_history) - 1:
                pdf.add_page_break()
        
        # Generer le PDF
        filepath = pdf.generate()
        
        print(f"\nRapport PDF genere avec succes!")
        print(f"Fichier: {filepath}")
        
    except Exception as e:
        print(f"\nErreur lors de la generation du PDF: {e}")
        import traceback
        traceback.print_exc()


def main():
    """
    Fonction principale qui lance l'application
    """
    print("\nTrading Analyzer - Demarrage...")
    print("Version finale - Projet M1 INFO IA DATA")
    
    # Variable globale pour stocker le portfolio
    global current_portfolio
    current_portfolio = None
    
    while True:
        afficher_menu()
        
        try:
            choix = input("\nVotre choix: ").strip()
            
            if choix == "1":
                analyser_action()
            elif choix == "2":
                afficher_actions_bdd()
            elif choix == "3":
                creer_portfolio_reel()
            elif choix == "4":
                creer_visualisations()
            elif choix == "5":
                generer_rapport_pdf()
            elif choix == "0":
                print("\nAu revoir ! Merci d'avoir utilise Trading Analyzer.")
                sys.exit(0)
            else:
                print("\nChoix invalide. Veuillez choisir une option du menu.")
        
        except KeyboardInterrupt:
            print("\n\nInterruption detectee. Au revoir !")
            sys.exit(0)
        except Exception as e:
            print(f"\nErreur: {e}")
            import traceback
            traceback.print_exc()
        
        input("\n[Appuyez sur Entree pour continuer]")


if __name__ == "__main__":
    main()