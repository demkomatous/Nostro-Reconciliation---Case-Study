-- Use this script after importing csv as table to DB Browser. It will format your table to structure required for practice

-- Create new table with the required structure (datatypes, primary key)
CREATE TABLE "Apex_International_Bank_transactions_new" (
    "tx_id" TEXT PRIMARY KEY,
    "date" DATE,
    "time" TIME,
    "sender_acc_number" TEXT,
    "beneficiary_iban" TEXT,
    "amount" INTEGER,
    "fee_type" TEXT,
    "catch" INTEGER
);

-- Move data to new table with boolean conversion
INSERT INTO "Apex_International_Bank_transactions_new"
    ("tx_id", "date", "time", "sender_acc_number", "beneficiary_iban", "amount", "fee_type", "catch")
SELECT
    "tx_id",
    "date",
    "time",
    "sender_acc_number",
    "beneficiary_iban",
    "amount",
    "fee_type",
    CASE
        WHEN "catch" = 'True' THEN 1
        WHEN "catch" = 'False' THEN 0
        ELSE NULL
    END AS "catch"
FROM "Apex_International_Bank_transactions";

-- Drop old table with wrong structure
DROP TABLE "Apex_International_Bank_transactions";

-- Rename new table to original name
ALTER TABLE "Apex_International_Bank_transactions_new"
RENAME TO "Apex_International_Bank_transactions";