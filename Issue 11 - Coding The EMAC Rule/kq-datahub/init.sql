-- Create table coins if it doesn't exist
CREATE TABLE IF NOT EXISTS coins (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    symbol VARCHAR(100),
    is_active INTEGER,
    first_historical_data TIMESTAMP,
    last_historical_data TIMESTAMP
);

-- Create table ohlcv if it doesn't exist
CREATE TABLE IF NOT EXISTS ohlcv (
    id SERIAL PRIMARY KEY,
    coin_id INTEGER REFERENCES coins(id),
    time_open TIMESTAMP,
    time_close TIMESTAMP,
    time_high TIMESTAMP,
    time_low TIMESTAMP,
    open DOUBLE PRECISION,
    high DOUBLE PRECISION,
    low DOUBLE PRECISION,
    close DOUBLE PRECISION,
    volume DOUBLE PRECISION,
    market_cap DOUBLE PRECISION,
    interval VARCHAR(120)
);

CREATE INDEX idx_coins_symbol ON coins(symbol);
CREATE INDEX idx_ohlcv_coin_id ON ohlcv(coin_id);