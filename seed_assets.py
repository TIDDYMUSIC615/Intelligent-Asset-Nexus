import os
import psycopg2
from dotenv import load_dotenv

# Load connection credentials
load_dotenv()
db_url = os.getenv("DATABASE_URL")

print("🌱 Injecting institutional watchlist assets into cloud database...")

# Your foundational multi-sector target matrix
initial_assets = [
    # Crypto Pairs
    ('BTCUSD', 'Bitcoin / US Dollar', 'crypto'),
    ('ETHUSD', 'Ethereum / US Dollar', 'crypto'),
    ('SOLUSD', 'Solana / US Dollar', 'crypto'),
    
    # Energy Sector ETFs & Equities
    ('XLE', 'Energy Select Sector SPDR Fund', 'etf'),
    ('XOM', 'Exxon Mobil Corporation', 'stock'),
    ('CVX', 'Chevron Corporation', 'stock'),
    
    # Space & Defense Sector ETFs
    ('UFO', 'Procure Space ETF', 'etf'),
    ('PPA', 'Invesco Aerospace & Defense ETF', 'etf'),
    ('ARKX', 'ARK Space Exploration & Innovation ETF', 'etf')
]

try:
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Insert ignore logic ensures duplicates don't break the script if rerun
    insert_query = """
    INSERT INTO assets (symbol, name, asset_type, is_tracked)
    VALUES (%s, %s, %s, TRUE)
    ON CONFLICT (symbol) DO NOTHING;
    """
    
    cursor.executemany(insert_query, initial_assets)
    conn.commit()
    
    # Verify rows inside database
    cursor.execute("SELECT COUNT(*) FROM assets;")
    total_count = cursor.fetchone()[0]
    
    print(f"🚀 Watchlist seeding complete! Total tracked assets in cloud: {total_count}")
    
    cursor.close()
    conn.close()

except Exception as e:
    print(f"❌ Seeding pipeline failed: {e}")