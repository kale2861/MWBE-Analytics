import duckdb
from pathlib import Path

# -----------------------------
# Define paths
# -----------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "processed"

DB_DIR = BASE_DIR / "database"

DB_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DB_PATH = DB_DIR / "mwbe_vendor_intelligence.duckdb"

# -----------------------------
# Connect to DuckDB
# -----------------------------

con = duckdb.connect(str(DB_PATH))

# -----------------------------
# Load MWBE enriched dataset
# -----------------------------

mwbe_file = (
    DATA_DIR
    / "mwbe_vendor_intelligence_enriched.csv"
)

con.execute(f"""
CREATE OR REPLACE TABLE mwbe_vendor_intelligence AS
SELECT *
FROM read_csv_auto('{mwbe_file}')
""")

# -----------------------------
# Load procurement features
# -----------------------------

procurement_file = (
    DATA_DIR
    / "vendor_procurement_features.csv"
)

con.execute(f"""
CREATE OR REPLACE TABLE vendor_procurement_features AS
SELECT *
FROM read_csv_auto('{procurement_file}')
""")

# -----------------------------
# Validate tables
# -----------------------------

tables = con.execute(
    "SHOW TABLES"
).fetchdf()

print("\nTables Loaded:")
print(tables)

# -----------------------------
# Row counts
# -----------------------------

mwbe_count = con.execute("""
SELECT COUNT(*)
FROM mwbe_vendor_intelligence
""").fetchone()[0]

procurement_count = con.execute("""
SELECT COUNT(*)
FROM vendor_procurement_features
""").fetchone()[0]

print(f"\nMWBE Rows: {mwbe_count}")
print(f"Procurement Rows: {procurement_count}")

# -----------------------------
# Sample query
# -----------------------------

sample_query = con.execute("""
SELECT
    naics_sector,
    COUNT(*) AS vendor_count
FROM mwbe_vendor_intelligence
GROUP BY naics_sector
ORDER BY vendor_count DESC
LIMIT 10
""").fetchdf()

print("\nTop Industries:")
print(sample_query)

# -----------------------------
# Close connection
# -----------------------------

con.close()

print("\nDuckDB load complete.")