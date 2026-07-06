"""
Generate a synthetic dataset for the Nostro reconciliation assignment.

The script initially creates error-free data and subsequently introduces specific
errors and discrepancies based on the 'catch' configuration. Comments and flags
alongside configuration variables map directly to the assignment guidelines.
Every 'catch' scenario corresponds to its description in the assignment documentation.
"""
import math
import os
import random
import time
import schwifty
import pandas as pd
import uuid

# Initial skript config
max_amount: int = 518
min_amount: int = 52  # Because of fee, keep over 10
generate_rows: int = 10000
# Catch configuration
catch_weekend_clearing_pct: float = 8  # OUTSTANDING_ITEM
catch_fee_pct: float = 2  # ERR_FEE_MISMATCH
catch_lost_transactions: int = 132  # ERR_MISSING_BOOKING
catch_misrouted_transaction_pct: float = 1.8  # ERR_MISROUTED_TRANSACTION
catch_unknown_money: int = 3  # EXPENSE, REVENUE (3 is fixed, do not change)
catch_unknown_customer: int = 15  # UNIDENTIFIED_CUSTOMER
catch_double_clearing_transactions: int = 16  # ERR_DOUBLE_POSTING
catch_amount_mismatch_pct: float = 1.5  # ERR_AMOUNT_MISMATCH

# Fundamental configs - do not change
sepa_fee: int = 10
start_time_s = 60 * 60 * 8  # 8:00
end_time_s = 60 * 60 * 16  # 16:00
date_rb = "2026-06-12"
date_db = "2026-06-15"
fee_types = ["OUR", "BEN", "SHA"]
weekend_clearing_time_start_s = 60 * 60 * 17
weekend_clearing_time_end_s = math.floor(60 * 60 * 23.9)
catch_unknown_money += catch_unknown_customer  # Catch for customers and unknown money is merged

unknown_customer_tmp_l = ["TRF FROM BNP BANK SA / CUSTOMER UNKNOWN"] * catch_unknown_customer
unknown_money_reasons = [
	"CHGS/PERIODIC/MAINTENANCE FEE MAY 2026",
	"INT.CALC/CREDIT INTEREST BASE VALUE",
	# "REV/ERRONEOUS BOOKING DELTA 2026-06-10", # Excluded
	"SEPA SETTLEMENT ADJUSTMENT NOTE"
] + unknown_customer_tmp_l

# Info variables
catch_indexes = []
start_time = time.time()

rb_list = []
db_list = []
zfill_len = len(str(generate_rows))

# Fill up lists
for i in range(generate_rows):
	uetr_id = str(uuid.uuid4())

	tx_time = time.strftime("%H:%M:%S", time.gmtime(random.randint(start_time_s, end_time_s)))
	sender_acc = f"{random.randint(100000000000, 999999999999)}/5432"
	beneficiary_iban = schwifty.IBAN.random()
	amount = random.randint(min_amount, max_amount)
	fee_type = random.choice(fee_types)

	rb_list.append([uetr_id, date_rb, tx_time, sender_acc, beneficiary_iban, amount, fee_type, False])

	cleared_amount = amount
	if fee_type == "BEN":
		cleared_amount -= sepa_fee

	ext_ref_id = f"EXTAIB_{date_db}_{str(i).zfill(zfill_len)}"
	db_list.append([ext_ref_id, date_db, f"Ref: {uetr_id}", cleared_amount, False])

# Construct dataframes
aib_data = pd.DataFrame(
	rb_list,
	columns=[
		"tx_id", "date", "time", "sender_acc_number", "beneficiary_iban", "amount", "fee_type", "catch"
	]
)
esb_data = pd.DataFrame(
	db_list,
	columns=[
		"ext_ref_id", "booking_date", "remittance_info", "cleared_amount", "catch"
	]
)

# Weekend clearing catch
aib_data_masked = aib_data[aib_data["catch"] == False]
transactions_count = math.floor(len(aib_data_masked) * (catch_weekend_clearing_pct / 100))
if transactions_count > 0:
	sample_data = aib_data_masked.sample(transactions_count)
	sample_idxs = list(sample_data.index)
	catch_indexes += sample_idxs
	print(f"Catch indexes for weekend: {sample_idxs}")

	new_times = [
		time.strftime(
			"%H:%M:%S",
			time.gmtime(
				random.randint(weekend_clearing_time_start_s, weekend_clearing_time_end_s)
			)
		) for _ in range(transactions_count)
	]
	aib_data.loc[sample_idxs, "time"] = new_times
	aib_data.loc[sample_idxs, "catch"] = True
	esb_data = esb_data.drop(sample_idxs, errors="ignore")

# Bank fees catch
aib_data_masked = aib_data[(aib_data["catch"] == False) & (aib_data["fee_type"].isin(["OUR", "SHA"]))]
transactions_count = math.floor(len(aib_data_masked) * (catch_fee_pct / 100))
if transactions_count > 0:
	sample_data = aib_data_masked.sample(transactions_count)
	sample_idxs = list(sample_data.index)
	catch_indexes += sample_idxs
	print(f"Catch indexes for fees: {sample_idxs}")

	esb_data.loc[sample_idxs, "cleared_amount"] -= sepa_fee
	esb_data.loc[sample_idxs, "catch"] = True
	aib_data.loc[sample_idxs, "catch"] = True

# Lost transaction catch
aib_data_masked = aib_data[aib_data["catch"] == False]
sample_data = aib_data_masked.sample(catch_lost_transactions)
sample_idxs = list(sample_data.index)
catch_indexes += sample_idxs
print(f"Catch indexes for lost transaction: {sample_idxs}")
esb_data = esb_data.drop(sample_idxs, errors="ignore")
aib_data.loc[sample_idxs, "catch"] = True

# Misrouted transaction catch (not verified)
aib_data_masked = aib_data[aib_data["catch"] == False]
transactions_count = math.floor(len(aib_data_masked) * (catch_misrouted_transaction_pct / 100))
sample_data = aib_data_masked.sample(transactions_count)
sample_idxs = list(sample_data.index)
catch_indexes += sample_idxs
print(f"Catch indexes for Misrouted transaction: {sample_idxs}")
esb_data.loc[sample_idxs, "catch"] = True
aib_data = aib_data.drop(sample_idxs)

# Unknown money catch
if catch_unknown_money > len(unknown_money_reasons):
	catch_unknown_money = len(unknown_money_reasons)

aib_data_masked = aib_data[aib_data["catch"] == False]
sample_data = aib_data_masked.sample(catch_unknown_money)
sample_idxs = list(sample_data.index)
catch_indexes += sample_idxs
print(f"Catch indexes for unknown transaction: {list(sample_data.index)}")
aib_data = aib_data.drop(sample_idxs)

unique_reasons = random.sample(unknown_money_reasons, catch_unknown_money)
esb_data.loc[sample_idxs, "catch"] = True
esb_data.loc[sample_idxs, "remittance_info"] = unique_reasons

# Double clearing catch
next_idx = esb_data.index.max() + 1 if not esb_data.empty else 0
aib_data_masked = aib_data[aib_data["catch"] == False]
sample_data = aib_data_masked.sample(catch_double_clearing_transactions)
sample_idxs = list(sample_data.index)
catch_indexes += sample_idxs
print(f"Catch indexes for double clearing: {list(sample_data.index)}")
for idx in sample_idxs:
	esb_data.loc[next_idx] = [
		f"EXT_{date_db}_{str(len(esb_data)).zfill(len(str(generate_rows)))}",
		date_db,
		f"Ref: {aib_data.loc[idx]['tx_id']}",
		aib_data.loc[idx]['amount'],
		False
	]
	aib_data.at[idx, "catch"] = True
	next_idx += 1

# Cleared amount mismatch catch
esb_data_masked = esb_data[(esb_data["catch"] == False)]
transactions_count = math.floor(len(esb_data_masked) * (catch_amount_mismatch_pct / 100))
if transactions_count > 0:
	sample_data = esb_data_masked.sample(transactions_count)
	sample_idxs = list(sample_data.index)
	catch_indexes += sample_idxs
	print(f"Catch indexes for cleared amount mismatch: {list(sample_idxs)}")

	random_amounts = [random.randint(min_amount, max_amount) for _ in range(transactions_count)]
	esb_data.loc[sample_idxs, "cleared_amount"] = random_amounts
	esb_data.loc[sample_idxs, "catch"] = True

	tx_ids_to_find = esb_data.loc[sample_idxs, "remittance_info"].str.replace("Ref: ", "", regex=False)
	aib_data.loc[aib_data["tx_id"].isin(tx_ids_to_find), "catch"] = True

# Runtime info
print(f"Catch indexes: {catch_indexes}")
print(f"Total catches: {len(catch_indexes)}")
print(f"Runtime: {time.time() - start_time}")

# Shuffle
aib_data = aib_data.sample(frac=1).reset_index(drop=True)
esb_data = esb_data.sample(frac=1).reset_index(drop=True)

# Save
ts = str(int(time.time()))
os.makedirs(f"Output/{ts}", exist_ok=True)
esb_data.to_csv(f"Output/{ts}/Eurozone_Settlement_Bank_statement.csv", index=False)
aib_data.to_csv(f"Output/{ts}/Apex_International_Bank_transactions.csv", index=False)
