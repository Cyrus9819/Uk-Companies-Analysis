"""
2_diagram_generator.py
======================
Companies House Data — SQL Query Runner & Chart Generator

Connects to the SQLite database produced by 1_data_cleaning.py,
executes 11 analytical queries, and saves charts to output_diagrams/.

Usage:
    python notebooks_or_scripts/2_diagram_generator.py
"""

import os
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
DB_PATH     = "data/cleaned/companies.db"
OUTPUT_DIR  = "output_diagrams"

os.makedirs(OUTPUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)
print(f"Connected to: {DB_PATH}\n")


# ─────────────────────────────────────────────
# HELPER — save or show
# ─────────────────────────────────────────────
def save(filename: str) -> None:
    path = os.path.join(OUTPUT_DIR, filename)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {path}")


# ─────────────────────────────────────────────
# Q1 — Company Status Distribution (Log Scale)
# ─────────────────────────────────────────────
print("Q1: Company status distribution...")
q1 = """
    SELECT CompanyStatus, COUNT(*) AS count
    FROM companies
    GROUP BY CompanyStatus
    ORDER BY count DESC;
"""
df1 = pd.read_sql_query(q1, conn)

plt.figure(figsize=(12, 6))
bars = plt.barh(df1.iloc[:, 0], df1.iloc[:, 1], color="steelblue", edgecolor="black")
plt.gca().invert_yaxis()
plt.xscale("log")
for bar in bars:
    w = bar.get_width()
    if w > 0:
        plt.text(w * 1.1, bar.get_y() + bar.get_height() / 2,
                 f"{int(w):,}", va="center", ha="left", fontsize=9, fontweight="bold")
plt.title("Distribution of Company Statuses (Log Scale)", fontsize=14, fontweight="bold")
plt.xlabel("Number of Companies (Logarithmic)", fontsize=12)
plt.ylabel("Company Status", fontsize=12)
plt.grid(axis="x", linestyle="--", alpha=0.4, which="both")
plt.tight_layout()
save("query_1_status.png")


# ─────────────────────────────────────────────
# Q2 — 2026 Incorporations KPI Tile
# ─────────────────────────────────────────────
print("Q2: 2026 incorporations milestone...")
q2 = """
    SELECT COUNT(*) AS incorporations_2026
    FROM companies
    WHERE substr(trim(IncorporationDate), 7, 4) = '2026';
"""
val_2026 = pd.read_sql_query(q2, conn).iloc[0, 0]

plt.figure(figsize=(5, 3))
plt.text(0.5, 0.62, f"{val_2026:,}", fontsize=38, fontweight="bold",
         ha="center", va="center", color="darkgreen")
plt.text(0.5, 0.28, "New Incorporations\nin 2026", fontsize=12,
         ha="center", va="center", color="gray")
plt.axis("off")
plt.title("2026 Milestone Indicator", fontsize=14, fontweight="bold")
plt.tight_layout()
save("query_2_milestone.png")


# ─────────────────────────────────────────────
# Q3 — Incorporation Volume Trends Over Time
# ─────────────────────────────────────────────
print("Q3: Incorporation volume trends...")
q3 = """
    SELECT substr(trim(IncorporationDate), 7, 4) AS year,
           COUNT(*) AS company_count
    FROM companies
    GROUP BY year
    ORDER BY year;
"""
df3 = pd.read_sql_query(q3, conn).dropna()
df3 = df3[df3.iloc[:, 0].str.strip() != ""]

plt.figure(figsize=(12, 5))
plt.plot(df3.iloc[:, 0], df3.iloc[:, 1], marker="o", color="crimson", linewidth=2)
plt.title("Incorporation Volume Trends Over Time", fontsize=14, fontweight="bold")
plt.xlabel("Year", fontsize=12)
plt.ylabel("Company Count", fontsize=12)
plt.xticks(rotation=45)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
save("query_3_trends.png")


# ─────────────────────────────────────────────
# Q4 — Annual Volume vs Cumulative Rolling Total
# ─────────────────────────────────────────────
print("Q4: Annual vs cumulative rolling total...")
q4 = """
    WITH yearly_data AS (
        SELECT substr(trim(IncorporationDate), 7, 4) AS year,
               COUNT(*) AS company_count
        FROM companies
        GROUP BY year
    )
    SELECT year,
           company_count,
           SUM(company_count) OVER (ORDER BY year) AS rolling_total
    FROM yearly_data
    ORDER BY year;
"""
df4 = pd.read_sql_query(q4, conn).dropna()
df4 = df4[df4.iloc[:, 0].str.strip() != ""]

fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.bar(df4.iloc[:, 0], df4.iloc[:, 1], color="lightblue", alpha=0.8,
        label="Annual Count")
ax1.set_xlabel("Year", fontsize=12)
ax1.set_ylabel("Annual Company Count", color="steelblue", fontsize=12)
ax1.tick_params(axis="y", labelcolor="steelblue")
plt.xticks(rotation=45)

ax2 = ax1.twinx()
ax2.plot(df4.iloc[:, 0], df4.iloc[:, 2], color="darkblue",
         marker="s", linewidth=2, label="Rolling Total")
ax2.set_ylabel("Cumulative Rolling Total", color="darkblue", fontsize=12)
ax2.tick_params(axis="y", labelcolor="darkblue")

plt.title("Annual Volume vs Cumulative Rolling Total", fontsize=14, fontweight="bold")
fig.tight_layout()
save("query_4_rolling.png")


# ─────────────────────────────────────────────
# Q5 — Number of Registered SIC Codes per Company
# ─────────────────────────────────────────────
print("Q5: SIC code count distribution...")
q5 = """
    SELECT sic_count, COUNT(*) AS company_count
    FROM (
        SELECT (
            CASE WHEN SICCode_SICText_1 IS NOT NULL AND TRIM(SICCode_SICText_1) <> '' THEN 1 ELSE 0 END +
            CASE WHEN SICCode_SICText_2 IS NOT NULL AND TRIM(SICCode_SICText_2) <> '' THEN 1 ELSE 0 END +
            CASE WHEN SICCode_SICText_3 IS NOT NULL AND TRIM(SICCode_SICText_3) <> '' THEN 1 ELSE 0 END +
            CASE WHEN SICCode_SICText_4 IS NOT NULL AND TRIM(SICCode_SICText_4) <> '' THEN 1 ELSE 0 END
        ) AS sic_count
        FROM companies
    )
    GROUP BY sic_count
    ORDER BY sic_count DESC;
"""
df5 = pd.read_sql_query(q5, conn)

plt.figure(figsize=(8, 5))
plt.bar(df5.iloc[:, 0].astype(str), df5.iloc[:, 1],
        color="mediumpurple", edgecolor="black")
plt.title("Number of Registered SIC Codes per Company", fontsize=14, fontweight="bold")
plt.xlabel("Number of SIC Codes Held (0–4)", fontsize=12)
plt.ylabel("Company Count", fontsize=12)
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
save("query_5_sic_count.png")


# ─────────────────────────────────────────────
# Q6 — Top 15 Company Categories (Log Scale)
# ─────────────────────────────────────────────
print("Q6: Top 15 company categories...")
q6 = """
    SELECT CompanyCategory, COUNT(*) AS total
    FROM companies
    GROUP BY CompanyCategory
    ORDER BY total DESC
    LIMIT 15;
"""
df6 = pd.read_sql_query(q6, conn)

plt.figure(figsize=(12, 6))
bars6 = plt.barh(df6.iloc[:, 0], df6.iloc[:, 1], color="teal", edgecolor="black")
plt.gca().invert_yaxis()
plt.xscale("log")
for bar in bars6:
    w = bar.get_width()
    if w > 0:
        plt.text(w * 1.1, bar.get_y() + bar.get_height() / 2,
                 f"{int(w):,}", va="center", ha="left", fontsize=9, fontweight="bold")
plt.title("Top 15 Company Categories (Log Scale)", fontsize=14, fontweight="bold")
plt.xlabel("Total Companies (Logarithmic)", fontsize=12)
plt.ylabel("Category", fontsize=12)
plt.grid(axis="x", linestyle="--", alpha=0.4, which="both")
plt.tight_layout()
save("query_6_categories.png")


# ─────────────────────────────────────────────
# Q7 — Top 10 Countries of Company Origin
# ─────────────────────────────────────────────
print("Q7: Top 10 countries of origin...")
q7 = """
    SELECT CountryOfOrigin AS country, COUNT(*) AS country_count
    FROM companies
    GROUP BY CountryOfOrigin
    ORDER BY country_count DESC
    LIMIT 10;
"""
df7 = pd.read_sql_query(q7, conn)

plt.figure(figsize=(11, 6))
bars7 = plt.barh(df7.iloc[:, 0], df7.iloc[:, 1],
                 color="forestgreen", edgecolor="black")
plt.gca().invert_yaxis()
plt.xscale("log")
for bar in bars7:
    w = bar.get_width()
    plt.text(w * 1.1, bar.get_y() + bar.get_height() / 2,
             f"{int(w):,}", va="center", ha="left", fontsize=10, fontweight="bold")
plt.title("Top 10 Countries of Company Origin (Log Scale)", fontsize=14, fontweight="bold")
plt.xlabel("Number of Companies (Logarithmic)", fontsize=12)
plt.ylabel("Country", fontsize=12)
plt.grid(axis="x", linestyle="--", alpha=0.4, which="both")
plt.tight_layout()
save("query_7_countries.png")


# ─────────────────────────────────────────────
# Q8 — Volume of Next Return Due Dates (Year-Wise)
# ─────────────────────────────────────────────
print("Q8: Next return due dates by year...")
q8 = """
    WITH yearly_data AS (
        SELECT substr(trim(Returns_NextDueDate), 7, 4) AS year,
               COUNT(*) AS company_count
        FROM companies
        GROUP BY year
    )
    SELECT year, company_count FROM yearly_data ORDER BY year;
"""
df8 = pd.read_sql_query(q8, conn).dropna()
df8 = df8[df8.iloc[:, 0].str.strip() != ""]

plt.figure(figsize=(12, 5))
plt.plot(df8.iloc[:, 0], df8.iloc[:, 1], marker="x", linestyle="--",
         color="darkorange", linewidth=2)
plt.title("Volume of Next Return Due Dates Year-Wise", fontsize=14, fontweight="bold")
plt.xlabel("Year", fontsize=12)
plt.ylabel("Company Count", fontsize=12)
plt.xticks(rotation=45)
plt.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
save("query_8_returns.png")


# ─────────────────────────────────────────────
# Q9 — Confirmation Statement Next Due Dates (Year-Wise)
# ─────────────────────────────────────────────
print("Q9: Confirmation statement due dates...")
q9 = """
    WITH year_data AS (
        SELECT strftime('%Y', ConfStmtNextDueDate) AS year,
               COUNT(*) AS company_count
        FROM companies
        GROUP BY year
    )
    SELECT year, company_count FROM year_data ORDER BY year;
"""
df9 = pd.read_sql_query(q9, conn).dropna()
df9 = df9[df9.iloc[:, 0].str.strip() != ""]

plt.figure(figsize=(12, 5))
plt.bar(df9.iloc[:, 0], df9.iloc[:, 1], color="salmon", edgecolor="black")
plt.title("Confirmation Statement Next Due Dates Year-Wise", fontsize=14, fontweight="bold")
plt.xlabel("Year", fontsize=12)
plt.ylabel("Company Count", fontsize=12)
plt.xticks(rotation=45)
plt.grid(axis="y", linestyle="--", alpha=0.5)
plt.tight_layout()
save("query_9_conf_stmt.png")


# ─────────────────────────────────────────────
# Q10 — Foreign Exception Indicator (KPI Tile)
# ─────────────────────────────────────────────
print("Q10: Foreign exception indicator...")
q10 = """
    SELECT COUNT(*) AS null_return_last_made_non_uk
    FROM companies
    WHERE CountryOfOrigin <> 'United Kingdom'
      AND Returns_LastMadeUpDate IS NULL;
"""
val_non_uk = pd.read_sql_query(q10, conn).iloc[0, 0]

plt.figure(figsize=(5, 3))
plt.text(0.5, 0.62, f"{val_non_uk:,}", fontsize=38, fontweight="bold",
         ha="center", va="center", color="darkred")
plt.text(0.5, 0.28, "Non-UK Companies with\nNull 'Last Made Up' Returns",
         fontsize=11, ha="center", va="center", color="gray")
plt.axis("off")
plt.title("Foreign Exception Indicator", fontsize=12, fontweight="bold")
plt.tight_layout()
save("query_10_foreign.png")


# ─────────────────────────────────────────────
# Q11 — Top 10 Most Common SIC Codes
# ─────────────────────────────────────────────
print("Q11: Top 10 most common SIC codes...")
q11 = """
    SELECT sic_code, COUNT(*) AS total
    FROM (
        SELECT TRIM(SICCode_SicText_1) AS sic_code FROM companies
        UNION ALL
        SELECT TRIM(SICCode_SicText_2) FROM companies
        UNION ALL
        SELECT TRIM(SICCode_SicText_3) FROM companies
        UNION ALL
        SELECT TRIM(SICCode_SicText_4) FROM companies
    )
    WHERE sic_code IS NOT NULL AND sic_code <> ''
    GROUP BY sic_code
    ORDER BY total DESC
    LIMIT 10;
"""
df11 = pd.read_sql_query(q11, conn)
labels = [
    (str(t)[:45] + "...") if len(str(t)) > 45 else str(t)
    for t in df11.iloc[:, 0]
]

plt.figure(figsize=(12, 6))
bars11 = plt.barh(labels, df11.iloc[:, 1], color="cadetblue", edgecolor="black")
plt.gca().invert_yaxis()
for bar in bars11:
    w = bar.get_width()
    plt.text(w * 1.02, bar.get_y() + bar.get_height() / 2,
             f"{int(w):,}", va="center", ha="left", fontsize=9, fontweight="bold")
plt.title("Top 10 Most Common SIC Codes (UK Company Structure)", fontsize=14, fontweight="bold")
plt.xlabel("Frequency Across All Registered Fields", fontsize=12)
plt.ylabel("SIC Code & Description", fontsize=12)
plt.grid(axis="x", linestyle="--", alpha=0.5)
plt.tight_layout()
save("query_11_top_sic.png")


# ─────────────────────────────────────────────
# DONE
# ─────────────────────────────────────────────
conn.close()
print(f"\n✅  All 11 charts saved to: {OUTPUT_DIR}/")
