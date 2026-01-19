-- Schéma de la base de données Trading Analyzer
-- Base de données SQLite

-- Table pour stocker les informations de base des actions
CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table pour stocker l'historique des prix
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
    UNIQUE(stock_id, date)  -- Une seule entrée par action et par jour
);

-- Table pour stocker les portfolios
CREATE TABLE IF NOT EXISTS portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table de liaison entre portfolios et actions (relation many-to-many)
CREATE TABLE IF NOT EXISTS portfolio_stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    portfolio_id INTEGER NOT NULL,
    stock_id INTEGER NOT NULL,
    quantity INTEGER DEFAULT 1,  -- Nombre d'actions possédées
    purchase_price REAL,          -- Prix d'achat
    purchase_date DATE,           -- Date d'achat
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (portfolio_id) REFERENCES portfolios(id) ON DELETE CASCADE,
    FOREIGN KEY (stock_id) REFERENCES stocks(id) ON DELETE CASCADE,
    UNIQUE(portfolio_id, stock_id)  -- Une action ne peut être qu'une fois dans un portfolio
);

-- Index pour améliorer les performances des requêtes fréquentes
CREATE INDEX IF NOT EXISTS idx_stock_prices_date ON stock_prices(date);
CREATE INDEX IF NOT EXISTS idx_stock_prices_stock_id ON stock_prices(stock_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_stocks_portfolio ON portfolio_stocks(portfolio_id);
CREATE INDEX IF NOT EXISTS idx_portfolio_stocks_stock ON portfolio_stocks(stock_id);

-- Vue pour faciliter la récupération des données complètes
CREATE VIEW IF NOT EXISTS v_portfolio_details AS
SELECT 
    p.id as portfolio_id,
    p.name as portfolio_name,
    s.symbol,
    s.name as stock_name,
    ps.quantity,
    ps.purchase_price,
    ps.purchase_date
FROM portfolios p
JOIN portfolio_stocks ps ON p.id = ps.portfolio_id
JOIN stocks s ON s.id = ps.stock_id;