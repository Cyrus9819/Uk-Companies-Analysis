"""
1_data_cleaning.py
==================
Companies House Data — End-to-End Cleaning & Preprocessing Pipeline

Input  : data/raw/BasicCompanyData-*.csv
Output : data/cleaned/companies_clean_full.csv
         data/cleaned/companies_clean_part_N.csv  (chunked, SQLite-friendly)
         data/cleaned/companies.db                (SQLite database)

Usage:
    python notebooks_or_scripts/1_data_cleaning.py
"""

import os
import re
import sqlite3

import numpy as np
import pandas as pd

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
INPUT_FILE = "data/raw/BasicCompanyData-2026-06-01-part1_7.csv"
OUTPUT_DIR = "data/cleaned"
CHUNK_SIZE = 200_000  # rows per output chunk (good for SQLite / DBeaver stability)

os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# 1. LOAD DATA
# ─────────────────────────────────────────────
print("Loading data...")
df = pd.read_csv(INPUT_FILE, low_memory=False)
print(f"  Original rows : {df.shape[0]:,}")
print(f"  Columns       : {df.shape[1]}")


# ─────────────────────────────────────────────
# 2. CLEAN COLUMN NAMES
# ─────────────────────────────────────────────
df.columns = (
    df.columns
    .str.strip()
    .str.replace(".", "_", regex=False)
    .str.replace(" ", "_", regex=False)
)


# ─────────────────────────────────────────────
# 3. DEDUPLICATE ON COMPANY NUMBER
# ─────────────────────────────────────────────
if "CompanyNumber" in df.columns:
    df["CompanyNumber"] = df["CompanyNumber"].astype(str).str.strip()
    before = len(df)
    df = df.drop_duplicates(subset="CompanyNumber")
    print(f"  Dropped {before - len(df):,} duplicate CompanyNumber rows")


# ─────────────────────────────────────────────
# 4. CLEAN COMPANY NAME
# ─────────────────────────────────────────────
df["CompanyName"] = (
    df["CompanyName"]
    .astype(str)
    .str.upper()
    .str.strip()
    .str.replace(r"^[^A-Z0-9]+", "", regex=True)  # strip leading symbols
    .str.replace(r"\s+", " ", regex=True)          # collapse whitespace
)


# ─────────────────────────────────────────────
# 5. CLEAN COUNTRY + CREATE COUNTRY GROUP
# ─────────────────────────────────────────────
if "RegAddress_Country" in df.columns:
    df["RegAddress_Country"] = (
        df["RegAddress_Country"]
        .astype(str)
        .str.upper()
        .str.strip()
    )
    df["CountryGroup"] = df["RegAddress_Country"].replace({
        "ENGLAND":          "UK",
        "SCOTLAND":         "UK",
        "WALES":            "UK",
        "NORTHERN IRELAND": "UK",
    })


# ─────────────────────────────────────────────
# 6. CLEAN POSTCODE
# ─────────────────────────────────────────────
if "RegAddress_PostCode" in df.columns:
    df["RegAddress_PostCode"] = (
        df["RegAddress_PostCode"]
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
    )


# ─────────────────────────────────────────────
# 7. BUILD FULL ADDRESS (SQL-FRIENDLY)
# ─────────────────────────────────────────────
address_parts = [
    "RegAddress_AddressLine1",
    "RegAddress_AddressLine2",
    "RegAddress_PostTown",
    "RegAddress_County",
    "RegAddress_PostCode",
]
for col in address_parts:
    if col not in df.columns:
        df[col] = ""

df["FullAddress"] = (
    df["RegAddress_AddressLine1"].fillna("") + ", "
    + df["RegAddress_AddressLine2"].fillna("") + ", "
    + df["RegAddress_PostTown"].fillna("") + ", "
    + df["RegAddress_PostCode"].fillna("")
)
df["FullAddress"] = df["FullAddress"].str.replace(r"(,\s*)+", ", ", regex=True)
df["FullAddress"] = df["FullAddress"].str.strip(", ")


# ─────────────────────────────────────────────
# 8. PARSE DATES (ISO FORMAT FOR SQL)
# ─────────────────────────────────────────────
date_cols = ["ConfStmtNextDueDate", "ConfStmtLastMadeUpDate"]
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], dayfirst=True, errors="coerce")


# ─────────────────────────────────────────────
# 9. BOOLEAN / DERIVED FLAGS
# ─────────────────────────────────────────────
df["HasPostcode"] = df["RegAddress_PostCode"].notna() & (df["RegAddress_PostCode"] != "NAN")
df["IsLondon"] = df["RegAddress_PostTown"].fillna("").str.contains("LONDON", case=False)


# ─────────────────────────────────────────────
# 10. DROP HEAVY COLUMNS (PreviousName fields)
# ─────────────────────────────────────────────
drop_cols = [c for c in df.columns if "PreviousName" in c]
df = df.drop(columns=drop_cols, errors="ignore")
print(f"  Dropped {len(drop_cols)} PreviousName columns")


# ─────────────────────────────────────────────
# 11. FINAL MEMORY CLEANUP
# ─────────────────────────────────────────────
df = df.replace([np.inf, -np.inf], np.nan)
print(f"  Cleaned rows  : {df.shape[0]:,}")


# ─────────────────────────────────────────────
# 12. SAVE FULL CLEAN FILE
# ─────────────────────────────────────────────
clean_file = os.path.join(OUTPUT_DIR, "companies_clean_full.csv")
df.to_csv(clean_file, index=False)
print(f"\nSaved full file : {clean_file}")


# ─────────────────────────────────────────────
# 13. SPLIT INTO CHUNKS (SQLITE STABLE IMPORTS)
# ─────────────────────────────────────────────
for i, start in enumerate(range(0, len(df), CHUNK_SIZE)):
    chunk = df.iloc[start : start + CHUNK_SIZE]
    chunk_file = os.path.join(OUTPUT_DIR, f"companies_clean_part_{i + 1}.csv")
    chunk.to_csv(chunk_file, index=False)
    print(f"Saved chunk     : {chunk_file}")


# ─────────────────────────────────────────────
# 14. WRITE TO SQLITE DATABASE
# ─────────────────────────────────────────────
db_path = os.path.join(OUTPUT_DIR, "companies.db")
print(f"\nWriting SQLite database: {db_path}")

conn = sqlite3.connect(db_path)
df.to_sql("companies", conn, if_exists="replace", index=False, chunksize=10_000)
conn.close()

print("\n✅  DONE — Clean dataset ready for analysis.")
print(f"    Rows : {len(df):,} | Columns : {df.shape[1]}")
