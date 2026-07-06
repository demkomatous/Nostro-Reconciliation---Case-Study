-- Use this script after importing csv as table to DB Browser. It will format your table to structure required for practice

-- Create new table with the required structure (datatypes, primary key)
CREATE TABLE "Eurozone_Settlement_Bank_statement_new" (
    "ext_ref_id" TEXT PRIMARY KEY,
    "booking_date" DATE,
    "remittance_info" TEXT,
    "cleared_amount" INTEGER,
    "catch" INTEGER
);

-- Move data to new table with boolean conversion
INSERT INTO "Eurozone_Settlement_Bank_statement_new"
    ("ext_ref_id", "booking_date", "remittance_info", "cleared_amount", "catch")
SELECT
    "ext_ref_id",
    "booking_date",
    "remittance_info",
    "cleared_amount",
    CASE
        WHEN TRIM(UPPER("catch")) = 'TRUE' THEN 1
        WHEN TRIM(UPPER("catch")) = 'FALSE' THEN 0
    END AS "catch"
FROM "Eurozone_Settlement_Bank_statement";

-- Drop old table with wrong structure
DROP TABLE "Eurozone_Settlement_Bank_statement";

-- Rename new table to original name
ALTER TABLE "Eurozone_Settlement_Bank_statement_new"
RENAME TO "Eurozone_Settlement_Bank_statement";