# 🇬🇧 UK Companies House — Data Analysis Pipeline

> End-to-end analytics project on **~850,000 UK registered companies** sourced from Companies House open data. Covers data ingestion, cleaning, SQL analysis, and visualisation.

---

## 📊 Key Findings at a Glance

| Metric | Value |
|---|---|
| Total companies analysed | 849,999 |
| Active companies | 774,315 |
| New incorporations in 2026 (YTD) | 49,553 |
| Non-UK companies with missing returns | 6,795 |
| Most dominant company type | Private Limited Company (780,405) |
| Top SIC sector | Other letting & operating of own property (72,603) |

---

## 📁 Repository Structure

```
uk-companies-analysis/
├── data/
│   ├── .gitignore          # Excludes large CSV/DB files from version control
│   └── README.md           # Instructions for downloading the source dataset
│
├── Pyhton scripts/
│   ├── 1_data_cleaning.py          # Full preprocessing & sanitisation pipeline
│   └── 2_diagram_generator.py      # SQL query runner + chart generator (11 queries)
│
├── SQL queries/
│   └── company_queries.sql         # All 11 production-ready SQL queries
│
├── output_diagrams/
│   ├── query_1_status.png          # Company status distribution (log scale)
│   ├── query_2_milestone.png       # 2026 new incorporations KPI tile
│   ├── query_3_trends.png          # Incorporation volume trends over time
│   ├── query_4_rolling.png         # Annual vs cumulative dual-axis chart
│   ├── query_5_sic_count.png       # SIC codes registered per company
│   ├── query_6_categories.png      # Top 15 company categories
│   ├── query_7_countries.png       # Top 10 countries of origin
│   ├── query_8_returns.png         # Next return due dates by year
│   ├── query_9_conf_stmt.png       # Confirmation statement due dates
│   ├── query_10_foreign.png        # Non-UK missing returns indicator
│   └── query_11_top_sic.png        # Top 10 most common SIC sectors
│
├── license
│
└── README.md                       # This file
```

---

## 🗂️ Dataset Source

**Companies House — Basic Company Data (Open Data)**

- 🔗 [Download from Companies House](https://download.companieshouse.gov.uk/en_output.html)
- File used: `BasicCompanyData-2026-06-01-part1_7.csv` (~65 MB)
- Licence: [Companies House Open Data Licence](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)

> ⚠️ Raw CSV and `.db` files are excluded from this repo via `.gitignore` due to file size. See [`data/README.md`](data/README.md) for download instructions.

---

## ⚙️ Setup & Usage

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/uk-companies-analysis.git
cd uk-companies-analysis
```

### 2. Install dependencies
```bash
pip install pandas numpy matplotlib sqlite3
```

### 3. Download the dataset
Follow instructions in [`data/README.md`](data/README.md), then place the CSV in `data/raw/`.

### 4. Run the cleaning pipeline
```bash
python notebooks_or_scripts/1_data_cleaning.py
```
Outputs a cleaned CSV + SQLite database to `data/cleaned/`.

### 5. Generate all diagrams
```bash
python notebooks_or_scripts/2_diagram_generator.py
```
Saves all 11 charts to `output_diagrams/`.

---

## 📈 Output Diagrams

### Company Status Distribution
Shows how ~850k companies break down by legal status — Active, Liquidation, Administration, etc. — on a log scale.

### Incorporation Volume Trends
Historic line chart from the earliest available records through 2026, revealing the rapid growth in UK company formation over the past decade.

### Annual Volume vs Cumulative Total
Dual-axis chart comparing year-on-year incorporation counts against the rolling total of all registered companies.

### Top 15 Company Categories
Private Limited Companies dominate at 780,405, followed by guarantee companies (25,969) and limited partnerships (10,781).

### Top 10 Countries of Origin
The UK accounts for 843,172 companies. The British Virgin Islands (1,382) and Jersey (1,057) are the leading overseas registrants.

### Top 10 Most Common SIC Sectors
Real estate and property management dominate — "Other letting and operating of own property" (68209) is the single most common sector at 72,603 registrations.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| Python 3.x | Core scripting |
| pandas | Data loading, cleaning, transformation |
| numpy | Numerical operations |
| SQLite3 | Embedded database for querying |
| matplotlib | Chart generation |
| SQL (SQLite dialect) | Analytical queries |

---

## 📋 SQL Queries Covered

| # | Query | Description |
|---|---|---|
| Q1 | Company Status Distribution | Count by status, ordered descending |
| Q2 | 2026 Incorporations | KPI: count of companies incorporated in 2026 |
| Q3 | Yearly Incorporation Trends | Group by incorporation year |
| Q4 | Annual + Cumulative Rolling Total | Window function over yearly data |
| Q5 | SIC Code Count per Company | How many SIC codes each company holds |
| Q6 | Top 15 Company Categories | By company category, log scale |
| Q7 | Top 10 Countries of Origin | By CountryOfOrigin field |
| Q8 | Next Return Due Dates | Annual breakdown of Returns_NextDueDate |
| Q9 | Confirmation Statement Due Dates | Annual breakdown of ConfStmtNextDueDate |
| Q10 | Foreign Exception Indicator | Non-UK companies with null last return |
| Q11 | Top 10 SIC Codes | Most common SIC descriptions across all 4 SIC fields |

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

---

## 📄 Licence

This project is licensed under the MIT Licence. The underlying dataset is published by Companies House under the [Open Government Licence v3.0](http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

---

*Built by [Cyrus Karki](https://github.com/YOUR_USERNAME) · Data sourced from Companies House Open Data · June 2026*
