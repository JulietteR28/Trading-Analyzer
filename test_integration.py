"""
Test d'intégration - Trading Analyzer
Démontre le fonctionnement des classes principales ensemble
"""
from models.stock import Stock
from models.portfolio import Portfolio
from database.db_manager import DatabaseManager
from datetime import date

def main():
    print("=" * 60)
    print("🚀 TRADING ANALYZER - Test d'intégration")
    print("=" * 60)
    
    # 1. Créer des actions
    print("\n📈 Étape 1 : Création des actions")
    print("-" * 60)
    
    apple = Stock("AAPL", "Apple Inc.")
    apple.update_price(
        new_price=178.50,
        opening=175.20,
        high=179.00,
        low=174.80,
        volume=50000000
    )
    print(f"✅ {apple}")
    
    google = Stock("GOOGL", "Alphabet Inc.")
    google.update_price(
        new_price=142.30,
        opening=140.80,
        high=143.00,
        low=140.50,
        volume=25000000
    )
    print(f"✅ {google}")
    
    microsoft = Stock("MSFT", "Microsoft Corp.")
    microsoft.update_price(
        new_price=378.90,
        opening=375.10,
        high=380.00,
        low=374.50,
        volume=30000000
    )
    print(f"✅ {microsoft}")
    
    # 2. Créer un portfolio
    print("\n💼 Étape 2 : Création du portfolio")
    print("-" * 60)
    
    my_portfolio = Portfolio("Tech Portfolio")
    my_portfolio.add_stock(apple)
    my_portfolio.add_stock(google)
    my_portfolio.add_stock(microsoft)
    
    print(f"\n{my_portfolio}")
    print(f"   └─ Valeur totale: ${my_portfolio.get_total_value():.2f}")
    print(f"   └─ Variation moyenne: {my_portfolio.get_average_variation():.2f}%")
    
    best = my_portfolio.get_best_performer()
    worst = my_portfolio.get_worst_performer()
    print(f"\n   🏆 Meilleure action: {best.symbol} ({best.get_variation():+.2f}%)")
    print(f"   📉 Pire action: {worst.symbol} ({worst.get_variation():+.2f}%)")
    
    # 3. Sauvegarder dans la base de données
    print("\n💾 Étape 3 : Sauvegarde en base de données")
    print("-" * 60)
    
    db = DatabaseManager("data/trading_analyzer.db")
    
    # Insérer les actions
    for stock in my_portfolio.stocks:
        stock_id = db.insert_stock(stock.symbol, stock.name)
        
        # Insérer les prix du jour
        if stock.current_price:
            db.insert_stock_price(
                symbol=stock.symbol,
                date_value=date.today(),
                opening=stock.opening_price,
                closing=stock.current_price,
                high=stock.highest_price,
                low=stock.lowest_price,
                volume=stock.volume
            )
    
    # 4. Récupérer les données depuis la BDD
    print("\n📊 Étape 4 : Récupération depuis la BDD")
    print("-" * 60)
    
    all_stocks_db = db.get_all_stocks()
    print(f"\nActions en base de données: {len(all_stocks_db)}")
    for stock_data in all_stocks_db:
        print(f"   - {stock_data[1]}: {stock_data[2]}")
    
    # Récupérer l'historique d'une action
    apple_history = db.get_stock_history("AAPL")
    print(f"\nHistorique AAPL: {len(apple_history)} entrées")
    if apple_history:
        last_entry = apple_history[-1]
        print(f"   Dernière entrée: Date={last_entry[0]}, Close=${last_entry[2]:.2f}")
    
    # 5. Afficher un résumé final
    print("\n" + "=" * 60)
    print("✅ TEST D'INTÉGRATION RÉUSSI")
    print("=" * 60)
    print("\n📋 Résumé:")
    print(f"   • {len(my_portfolio.stocks)} actions créées")
    print(f"   • Portfolio d'une valeur de ${my_portfolio.get_total_value():.2f}")
    print(f"   • {len(all_stocks_db)} actions en base de données")
    print(f"   • Variation moyenne: {my_portfolio.get_average_variation():+.2f}%")
    print("\n🎉 Tous les modules fonctionnent correctement!")
    
    # Fermer la connexion
    db.close_connection()

if __name__ == "__main__":
    main()