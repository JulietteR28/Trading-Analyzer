# -*- coding: utf-8 -*-
"""
Interface Streamlit - Trading Analyzer
Interface graphique moderne et simple
"""
import streamlit as st
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api.data_fetcher import DataFetcher
from models.portfolio import Portfolio
from analysis.statistics import Analyzer
from analysis.indicators import TechnicalIndicators
from visualization.charts import ChartGenerator
from utils.action_dict import ACTIONS_LISTE, rechercher_action
import matplotlib.pyplot as plt

# Configuration de la page
st.set_page_config(
    page_title="Trading Analyzer",
    page_icon="📊",
    layout="wide"
)

# Titre principal
st.title("📊 Trading Analyzer")
st.markdown("---")

# Initialiser les objets (avec cache pour performance)
@st.cache_resource
def get_fetcher():
    return DataFetcher()

@st.cache_resource
def get_chart_gen():
    return ChartGenerator()

fetcher = get_fetcher()
chart_gen = get_chart_gen()

# Sidebar - Menu
st.sidebar.title("Menu")
page = st.sidebar.radio(
    "Navigation",
    ["🏠 Accueil", "📈 Analyse d'action", "💼 Portfolio", "📄 Générer rapport"]
)

st.sidebar.markdown("---")
st.sidebar.info("Projet M1 - Trading Analyzer\n\nAnalyse technique et financière")

# ========== PAGE 1 : ACCUEIL ==========
if page == "🏠 Accueil":
    st.header("Bienvenue sur Trading Analyzer")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("📈 **Analyse technique**\n\nRSI, moyennes mobiles, tendances")
    
    with col2:
        st.success("📊 **Visualisations**\n\nGraphiques interactifs et professionnels")
    
    with col3:
        st.warning("📄 **Rapports PDF**\n\nGénération automatique de rapports")
    
    st.markdown("---")
    
    st.subheader("Fonctionnalités")
    
    st.write("✅ **Analyse d'action** : Recherchez n'importe quelle action et obtenez une analyse complète")
    st.write("✅ **Portfolio** : Créez et gérez votre portfolio d'actions")
    st.write("✅ **Graphiques** : Visualisations avec moyennes mobiles et indicateurs")
    st.write("✅ **Indicateurs techniques** : RSI, signaux d'achat/vente, tendances")
    
    st.info("👈 Utilisez le menu à gauche pour naviguer dans l'application")

# ========== PAGE 2 : ANALYSE D'ACTION ==========
elif page == "📈 Analyse d'action":
    st.header("Analyse détaillée d'une action")
    
    # Choix du mode de saisie
    mode = st.radio("Mode de recherche", ["🔍 Recherche par nom", "⌨️ Saisie manuelle du symbole"], horizontal=True)
    
    symbol = None
    
    if mode == "🔍 Recherche par nom":
        # Sélection dans la liste
        selected_name = st.selectbox(
            "Choisissez une action",
            options=[""] + ACTIONS_LISTE,
            index=0,
            help="Sélectionnez une action dans la liste"
        )
        
        if selected_name:
            symbol = rechercher_action(selected_name)
            st.info(f"📊 Action sélectionnée: **{selected_name}** → Symbole: **{symbol}**")
    
    else:
        # Saisie manuelle
        symbol_input = st.text_input(
            "Symbole de l'action",
            "",
            max_chars=10,
            help="Exemple: AAPL, GOOGL, MSFT"
        ).upper()
        
        if symbol_input:
            symbol = symbol_input
    
    # Bouton d'analyse
    st.markdown("---")
    
    analyze_btn = st.button("🔍 Analyser", type="primary", disabled=(symbol is None or symbol == ""))
    
    if analyze_btn and symbol:
        with st.spinner(f"Analyse de {symbol} en cours..."):
            try:
                # Récupérer les données
                stock = fetcher.create_stock_from_api(symbol)
                
                if stock:
                    # Afficher les infos principales
                    st.success(f"✅ {stock.name}")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Prix actuel", f"${stock.current_price:.2f}")
                    
                    with col2:
                        st.metric("Variation", f"{stock.get_variation():.2f}%", 
                                 delta=f"{stock.get_variation():.2f}%")
                    
                    with col3:
                        if stock.highest_price:
                            st.metric("Plus haut", f"${stock.highest_price:.2f}")
                    
                    with col4:
                        if stock.lowest_price:
                            st.metric("Plus bas", f"${stock.lowest_price:.2f}")
                    
                    st.markdown("---")
                    
                    # Récupérer l'historique
                    hist = fetcher.fetch_historical_data(symbol, period="3mo")
                    
                    if hist is not None and not hist.empty:
                        # Analyse
                        analyzer = Analyzer(hist)
                        indicators = TechnicalIndicators(hist)
                        
                        # Graphique
                        st.subheader("📈 Graphique de prix avec moyenne mobile")
                        
                        ma = analyzer.calculate_moving_average(20)
                        fig = chart_gen.create_price_with_ma(
                            hist, ma,
                            f"Prix de {symbol} - 3 derniers mois",
                            window=20
                        )
                        st.pyplot(fig)
                        plt.close()
                        
                        st.markdown("---")
                        
                        # Statistiques et indicateurs
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.subheader("📊 Statistiques")
                            stats = analyzer.get_statistics()
                            
                            st.write(f"**Prix moyen (3 mois):** ${stats['prix_moyen']:.2f}")
                            st.write(f"**Prix minimum:** ${stats['prix_min']:.2f}")
                            st.write(f"**Prix maximum:** ${stats['prix_max']:.2f}")
                            
                            vol = analyzer.calculate_volatility()
                            if vol:
                                st.write(f"**Volatilité:** {vol:.2f}%")
                            
                            trend = analyzer.calculate_trend()
                            trend_emoji = "📈" if trend == "HAUSSE" else "📉" if trend == "BAISSE" else "➡️"
                            st.write(f"**Tendance:** {trend_emoji} {trend}")
                        
                        with col2:
                            st.subheader("🎯 Indicateurs techniques")
                            
                            rsi = indicators.calculate_rsi()
                            if rsi:
                                st.write(f"**RSI (14 jours):** {rsi:.2f}")
                                
                                if rsi < 30:
                                    st.success("🟢 Survendu - Opportunité d'achat potentielle")
                                elif rsi > 70:
                                    st.error("🔴 Suracheté - Attention à la surcote")
                                else:
                                    st.info("⚪ Zone normale")
                            
                            st.write("")
                            
                            signal = indicators.get_simple_signal()
                            
                            if signal == "ACHETER":
                                st.success(f"**Signal:** 🟢 {signal}")
                            elif signal == "VENDRE":
                                st.error(f"**Signal:** 🔴 {signal}")
                            else:
                                st.warning(f"**Signal:** ⏸️ {signal}")
                    
                    else:
                        st.warning("⚠️ Impossible de récupérer l'historique")
                
                else:
                    st.error(f"❌ Action '{symbol}' introuvable. Vérifiez le symbole.")
            
            except Exception as e:
                st.error(f"❌ Erreur lors de l'analyse : {str(e)}")

# ========== PAGE 3 : PORTFOLIO ==========
elif page == "💼 Portfolio":
    st.header("Gestion de Portfolio")
    
    # Initialiser le portfolio dans la session
    if 'portfolio' not in st.session_state:
        st.session_state.portfolio = Portfolio("Mon Portfolio")
    
    portfolio = st.session_state.portfolio
    
    # Ajouter une action
    st.subheader("➕ Ajouter une action")
    
    # Choix du mode
    mode_portfolio = st.radio(
        "Mode d'ajout",
        ["🔍 Liste d'actions", "⌨️ Saisie manuelle"],
        horizontal=True,
        key="portfolio_mode"
    )
    
    new_symbol = None
    
    if mode_portfolio == "🔍 Liste d'actions":
        col1, col2 = st.columns([3, 1])
        
        with col1:
            selected_action = st.selectbox(
                "Choisissez une action à ajouter",
                options=[""] + ACTIONS_LISTE,
                key="portfolio_select"
            )
        
        with col2:
            st.write("")
            st.write("")
            add_btn = st.button("➕ Ajouter", key="add_from_list")
        
        if add_btn and selected_action:
            new_symbol = rechercher_action(selected_action)
    
    else:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            new_symbol_input = st.text_input("Symbole", "", key="add_symbol").upper()
        
        with col2:
            st.write("")
            st.write("")
            add_btn = st.button("➕ Ajouter", key="add_from_input")
        
        if add_btn and new_symbol_input:
            new_symbol = new_symbol_input
    
    if new_symbol:
        with st.spinner(f"Ajout de {new_symbol}..."):
            try:
                stock = fetcher.create_stock_from_api(new_symbol)
                if stock:
                    portfolio.add_stock(stock)
                    st.success(f"✅ {new_symbol} ajouté au portfolio")
                else:
                    st.error(f"❌ Action '{new_symbol}' introuvable")
            except Exception as e:
                st.error(f"Erreur : {str(e)}")
    
    st.markdown("---")
    
    # Afficher le portfolio
    if portfolio.get_stocks_count() > 0:
        st.subheader(f"📊 {portfolio.name}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Nombre d'actions", portfolio.get_stocks_count())
        
        with col2:
            st.metric("Valeur totale", f"${portfolio.get_total_value():.2f}")
        
        with col3:
            st.metric("Variation moyenne", 
                     f"{portfolio.get_average_variation():.2f}%",
                     delta=f"{portfolio.get_average_variation():.2f}%")
        
        st.markdown("---")
        
        # Tableau des actions
        st.subheader("Actions du portfolio")
        
        data = []
        for stock in portfolio.stocks:
            data.append({
                "Symbole": stock.symbol,
                "Nom": stock.name,
                "Prix": f"${stock.current_price:.2f}",
                "Variation": f"{stock.get_variation():+.2f}%"
            })
        
        st.dataframe(data, use_container_width=True)
        
        # Meilleure et pire performance
        if portfolio.get_stocks_count() > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                best = portfolio.get_best_performer()
                st.success(f"🏆 **Meilleure:** {best.symbol} ({best.get_variation():+.2f}%)")
            
            with col2:
                worst = portfolio.get_worst_performer()
                st.info(f"📉 **Moins bonne:** {worst.symbol} ({worst.get_variation():+.2f}%)")
    
    else:
        st.info("📭 Portfolio vide. Ajoutez des actions ci-dessus.")

# ========== PAGE 4 : GENERER RAPPORT ==========
elif page == "📄 Générer rapport":
    st.header("Générer un rapport PDF")
    
    st.write("Cette fonctionnalité génère un rapport PDF complet avec :")
    st.write("- ✅ Analyse de plusieurs actions")
    st.write("- ✅ Graphiques de comparaison")
    st.write("- ✅ Statistiques et indicateurs techniques")
    st.write("- ✅ Mise en page professionnelle")
    
    st.markdown("---")
    
    st.subheader("📝 Configuration du rapport")
    
    # Mode de sélection
    mode_rapport = st.radio(
        "Mode de sélection des actions",
        ["🔍 Sélection dans la liste", "⌨️ Saisie manuelle"],
        horizontal=True,
        key="rapport_mode"
    )
    
    st.write("**Actions à inclure dans le rapport :**")
    
    if mode_rapport == "🔍 Sélection dans la liste":
        # Sélection multiple
        actions_selectionnees = st.multiselect(
            "Choisissez 1 à 5 actions",
            options=ACTIONS_LISTE,
            default=["Apple", "Google", "Microsoft"],
            max_selections=5,
            help="Sélectionnez jusqu'à 5 actions"
        )
        
        # Convertir en symboles
        symbols = [rechercher_action(nom) for nom in actions_selectionnees]
    
    else:
        # Saisie manuelle
        col1, col2, col3 = st.columns(3)
        
        with col1:
            action1 = st.text_input("Action 1", "AAPL", key="rapport_1")
        with col2:
            action2 = st.text_input("Action 2", "GOOGL", key="rapport_2")
        with col3:
            action3 = st.text_input("Action 3", "MSFT", key="rapport_3")
        
        symbols = [s.upper().strip() for s in [action1, action2, action3] if s.strip()]
    
    # Bouton de génération
    st.markdown("---")
    
    if st.button("🚀 Générer le rapport PDF", type="primary"):
        
        if len(symbols) == 0:
            st.error("❌ Veuillez entrer au moins une action")
        else:
            with st.spinner(f"Génération du rapport pour {', '.join(symbols)}... Cela peut prendre 30-60 secondes..."):
                try:
                    from api.data_fetcher import DataFetcher
                    from models.portfolio import Portfolio
                    from analysis.statistics import Analyzer
                    from analysis.indicators import TechnicalIndicators
                    from visualization.charts import ChartGenerator
                    from reports.pdf_generator import PDFGenerator
                    from reportlab.lib.units import cm
                    from datetime import datetime
                    import matplotlib.pyplot as plt
                    
                    # Créer les dossiers nécessaires
                    os.makedirs('data/exports', exist_ok=True)
                    
                    # Initialiser
                    fetcher = DataFetcher()
                    chart_gen = ChartGenerator()
                    
                    # Progress bar
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # 1. Récupérer les données
                    status_text.text("📥 Récupération des données...")
                    stocks = []
                    stocks_history = {}
                    
                    for i, symbol in enumerate(symbols):
                        progress_bar.progress((i + 1) / (len(symbols) * 3))
                        
                        stock = fetcher.create_stock_from_api(symbol)
                        if stock:
                            stocks.append(stock)
                        
                        hist = fetcher.fetch_historical_data(symbol, period="3mo")
                        if hist is not None and not hist.empty:
                            stocks_history[symbol] = hist
                    
                    if len(stocks) == 0:
                        st.error("❌ Aucune action valide trouvée")
                    else:
                        # 2. Créer les graphiques
                        status_text.text("📊 Création des graphiques...")
                        graph_files = []
                        
                        # Graphique de comparaison
                        if len(stocks_history) > 1:
                            fig_comp = chart_gen.create_comparison_chart(
                                stocks_history,
                                "Comparaison des performances (3 mois)"
                            )
                            chart_gen.save_chart(fig_comp, "rapport_comparaison.png")
                            graph_files.append("data/exports/rapport_comparaison.png")
                            plt.close()
                        
                        # Graphiques individuels
                        for j, symbol in enumerate(symbols):
                            if symbol in stocks_history:
                                progress_bar.progress((len(symbols) + j + 1) / (len(symbols) * 3))
                                
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
                                plt.close()
                        
                        chart_gen.close_all()
                        
                        # 3. Générer le PDF
                        status_text.text("📄 Génération du PDF...")
                        progress_bar.progress(0.8)
                        
                        pdf = PDFGenerator("rapport_portfolio.pdf")
                        
                        # Page de couverture
                        pdf.add_title_page(
                            "Rapport d'Analyse de Portfolio",
                            "Trading Analyzer - Analyse technique et financiere"
                        )
                        
                        # Section 1 : Résumé
                        pdf.add_heading("1. Resume du Portfolio")
                        pdf.add_text(f"Date du rapport: <b>{datetime.now().strftime('%d/%m/%Y %H:%M')}</b>")
                        pdf.add_text(f"Nombre d'actions: <b>{len(stocks)}</b>")
                        
                        pdf.add_spacer()
                        
                        # Tableau des actions
                        table_data = [['Symbole', 'Nom', 'Prix actuel', 'Variation']]
                        for stock in stocks:
                            table_data.append([
                                stock.symbol,
                                stock.name[:30],
                                f"${stock.current_price:.2f}",
                                f"{stock.get_variation():+.2f}%"
                            ])
                        
                        pdf.add_table(table_data, col_widths=[3*cm, 7*cm, 3*cm, 3*cm])
                        
                        # Section 2 : Graphique de comparaison
                        if len(graph_files) > 0 and len(stocks_history) > 1:
                            pdf.add_page_break()
                            pdf.add_heading("2. Comparaison des Performances")
                            pdf.add_text("Les prix sont normalises (base 100) pour faciliter la comparaison.")
                            pdf.add_spacer()
                            pdf.add_image(graph_files[0], width=10*cm, height=7*cm)
                        
                        # Section 3 : Analyses détaillées
                        pdf.add_page_break()
                        pdf.add_heading("3. Analyse Detaillee par Action")
                        
                        for i, symbol in enumerate(symbols):
                            if symbol not in stocks_history:
                                continue
                            
                            stock = next((s for s in stocks if s.symbol == symbol), None)
                            if stock:
                                pdf.add_text(f"<b>{symbol} - {stock.name}</b>")
                            
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
                            pdf.add_text(f"<b>Signal de trading: {signal}</b>")
                            
                            pdf.add_spacer()
                            
                            # Graphique
                            graph_index = i + (1 if len(stocks_history) > 1 else 0)
                            if graph_index < len(graph_files):
                                pdf.add_image(graph_files[graph_index], width=10*cm, height=7*cm)
                            
                            if i < len(symbols) - 1:
                                pdf.add_page_break()
                        
                        # Générer le PDF final
                        filepath = pdf.generate()
                        
                        progress_bar.progress(1.0)
                        status_text.text("✅ Rapport généré avec succès !")
                        
                        # Afficher le succès
                        st.success(f"✅ Rapport PDF généré avec succès !")
                        st.info(f"📁 Fichier : `{filepath}`")
                        
                        # Bouton de téléchargement
                        with open(filepath, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                            st.download_button(
                                label="📥 Télécharger le rapport PDF",
                                data=pdf_bytes,
                                file_name="rapport_portfolio.pdf",
                                mime="application/pdf"
                            )
                        
                        st.balloons()
                
                except Exception as e:
                    st.error(f"❌ Erreur lors de la génération : {str(e)}")
                    st.code(str(e))
                    import traceback
                    st.code(traceback.format_exc())

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>"
    "Trading Analyzer - Projet M1 INFO IA DATA | "
    "Données fournies par Yahoo Finance"
    "</div>",
    unsafe_allow_html=True
)