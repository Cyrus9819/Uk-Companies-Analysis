-- ============================================================
-- company_queries.sql
-- Companies House Open Data — Analytical Query Suite
-- Database: companies.db (SQLite)
-- Table: companies
-- Generated: June 2026
-- ============================================================


-- ──────────────────────────────────────────────────────────
-- Q1: Distribution of Company Statuses
-- Purpose: Understand the breakdown of all registered statuses
-- ──────────────────────────────────────────────────────────
SELECT
    CompanyStatus,
    COUNT(*) AS company_count
FROM companies
GROUP BY CompanyStatus
ORDER BY company_count DESC;


-- ──────────────────────────────────────────────────────────
-- Q2: New Incorporations in 2026 (KPI)
-- Purpose: Count companies incorporated in the current year
-- ──────────────────────────────────────────────────────────
SELECT
    COUNT(*) AS incorporations_2026
FROM companies
WHERE substr(trim(IncorporationDate), 7, 4) = '2026';


-- ──────────────────────────────────────────────────────────
-- Q3: Incorporation Volume Trends Over Time
-- Purpose: Year-by-year count of new registrations
-- ──────────────────────────────────────────────────────────
SELECT
    substr(trim(IncorporationDate), 7, 4) AS year,
    COUNT(*) AS company_count
FROM companies
GROUP BY year
ORDER BY year;


-- ──────────────────────────────────────────────────────────
-- Q4: Annual Volume vs Cumulative Rolling Total
-- Purpose: Track year-on-year growth and cumulative company stock
-- ──────────────────────────────────────────────────────────
WITH yearly_data AS (
    SELECT
        substr(trim(IncorporationDate), 7, 4) AS year,
        COUNT(*) AS company_count
    FROM companies
    GROUP BY year
)
SELECT
    year,
    company_count,
    SUM(company_count) OVER (ORDER BY year) AS rolling_total
FROM yearly_data
ORDER BY year;


-- ──────────────────────────────────────────────────────────
-- Q5: Number of Registered SIC Codes per Company
-- Purpose: Understand how many industry codes companies register
-- ──────────────────────────────────────────────────────────
SELECT
    sic_count,
    COUNT(*) AS company_count
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


-- ──────────────────────────────────────────────────────────
-- Q6: Top 15 Company Categories
-- Purpose: Identify dominant legal structures in the registry
-- ──────────────────────────────────────────────────────────
SELECT
    CompanyCategory,
    COUNT(*) AS total
FROM companies
GROUP BY CompanyCategory
ORDER BY total DESC
LIMIT 15;


-- ──────────────────────────────────────────────────────────
-- Q7: Top 10 Countries of Company Origin
-- Purpose: Map where registered companies originally come from
-- ──────────────────────────────────────────────────────────
SELECT
    CountryOfOrigin AS country,
    COUNT(*) AS country_count
FROM companies
GROUP BY CountryOfOrigin
ORDER BY country_count DESC
LIMIT 10;


-- ──────────────────────────────────────────────────────────
-- Q8: Volume of Next Return Due Dates (Year-Wise)
-- Purpose: Forecast annual compliance load for returns
-- ──────────────────────────────────────────────────────────
WITH yearly_data AS (
    SELECT
        substr(trim(Returns_NextDueDate), 7, 4) AS year,
        COUNT(*) AS company_count
    FROM companies
    GROUP BY year
)
SELECT year, company_count
FROM yearly_data
ORDER BY year;


-- ──────────────────────────────────────────────────────────
-- Q9: Confirmation Statement Next Due Dates (Year-Wise)
-- Purpose: Forecast annual compliance load for conf. statements
-- ──────────────────────────────────────────────────────────
WITH year_data AS (
    SELECT
        strftime('%Y', ConfStmtNextDueDate) AS year,
        COUNT(*) AS company_count
    FROM companies
    GROUP BY year
)
SELECT year, company_count
FROM year_data
ORDER BY year;


-- ──────────────────────────────────────────────────────────
-- Q10: Foreign Exception Indicator
-- Purpose: Identify non-UK companies with missing return history
--          (potential data quality / compliance gap)
-- ──────────────────────────────────────────────────────────
SELECT
    COUNT(*) AS null_return_last_made_non_uk
FROM companies
WHERE CountryOfOrigin <> 'United Kingdom'
  AND Returns_LastMadeUpDate IS NULL;


-- ──────────────────────────────────────────────────────────
-- Q11: Top 10 Most Common SIC Codes
-- Purpose: Find the most registered business sectors across
--          all four SIC code fields
-- ──────────────────────────────────────────────────────────
SELECT
    sic_code,
    COUNT(*) AS total
FROM (
    SELECT TRIM(SICCode_SicText_1) AS sic_code FROM companies
    UNION ALL
    SELECT TRIM(SICCode_SicText_2)              FROM companies
    UNION ALL
    SELECT TRIM(SICCode_SicText_3)              FROM companies
    UNION ALL
    SELECT TRIM(SICCode_SicText_4)              FROM companies
)
WHERE sic_code IS NOT NULL
  AND sic_code <> ''
GROUP BY sic_code
ORDER BY total DESC
LIMIT 10;
