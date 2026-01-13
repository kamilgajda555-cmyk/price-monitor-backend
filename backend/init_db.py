"""
Database initialization script - creates aggregation tables
"""
from app.models.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SQL = """
-- Daily Price Stats
CREATE TABLE IF NOT EXISTS daily_price_stats (
    id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    source_id INTEGER REFERENCES sources(id) ON DELETE CASCADE,
    stat_date DATE NOT NULL,
    min_price NUMERIC(10,2),
    max_price NUMERIC(10,2),
    avg_price NUMERIC(10,2),
    price_change NUMERIC(10,2),
    check_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(product_id, source_id, stat_date)
);

-- Source Daily Stats
CREATE TABLE IF NOT EXISTS source_daily_stats (
    id SERIAL PRIMARY KEY,
    source_id INTEGER NOT NULL REFERENCES sources(id) ON DELETE CASCADE,
    stat_date DATE NOT NULL,
    total_checks INTEGER DEFAULT 0,
    successful_checks INTEGER DEFAULT 0,
    failed_checks INTEGER DEFAULT 0,
    avg_price NUMERIC(10,2),
    success_rate NUMERIC(5,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source_id, stat_date)
);

-- Add cache columns to product_sources
ALTER TABLE product_sources 
    ADD COLUMN IF NOT EXISTS price_change_1d NUMERIC(10,2),
    ADD COLUMN IF NOT EXISTS price_change_7d NUMERIC(10,2),
    ADD COLUMN IF NOT EXISTS price_change_30d NUMERIC(10,2);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_daily_price_stats_product_date 
    ON daily_price_stats(product_id, stat_date DESC);
CREATE INDEX IF NOT EXISTS idx_daily_price_stats_source_date 
    ON daily_price_stats(source_id, stat_date DESC);
CREATE INDEX IF NOT EXISTS idx_source_daily_stats_source_date 
    ON source_daily_stats(source_id, stat_date DESC);
CREATE INDEX IF NOT EXISTS idx_price_history_product_date 
    ON price_history(product_id, checked_at DESC);
CREATE INDEX IF NOT EXISTS idx_price_history_lookup 
    ON price_history(product_id, source_id, checked_at DESC);
CREATE INDEX IF NOT EXISTS idx_price_history_product_id 
    ON price_history(product_id);
CREATE INDEX IF NOT EXISTS idx_price_history_source_id 
    ON price_history(source_id);
CREATE INDEX IF NOT EXISTS idx_alerts_user_id 
    ON alerts(user_id);
CREATE INDEX IF NOT EXISTS idx_alerts_product_id 
    ON alerts(product_id);
"""

def init_database():
    """Initialize database with aggregation tables"""
    try:
        logger.info("🚀 Initializing database tables...")
        
        with engine.connect() as conn:
            # Split SQL into individual statements
            statements = [s.strip() for s in SQL.split(';') if s.strip()]
            
            for statement in statements:
                try:
                    conn.execute(statement)
                    conn.commit()
                    
                    # Log table/index creation
                    if 'CREATE TABLE' in statement:
                        table = statement.split('CREATE TABLE IF NOT EXISTS')[1].split('(')[0].strip()
                        logger.info(f"   ✅ Table: {table}")
                    elif 'CREATE INDEX' in statement:
                        index = statement.split('CREATE INDEX IF NOT EXISTS')[1].split('ON')[0].strip()
                        logger.info(f"   ✅ Index: {index}")
                except Exception as e:
                    if 'already exists' not in str(e).lower():
                        logger.warning(f"   ⚠️  {e}")
        
        logger.info("✅ Database initialization complete!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    init_database()
