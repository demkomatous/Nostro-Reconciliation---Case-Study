# Assignment: interbanking reconciliation (Nostro / Clearing)

## Introduction to Nostro accounts

For the banks to be able to operate with foreign currencies, banks must have accounts with other banks, where that foreign currency is the domestic currency. They maintain accounts with these counterparties, known as Nostro accounts, through which foreign-currency transactions are settled. In our case, the domestic bank is Apex International Bank (AIB) which, for the purpose of this assignment, holds its EUR Nostro account with the German Eurozone Settlement Bank (ESB).

Every day, AIB's clients want to send euros worldwide. Each transaction is processed as follows:

1. Client initiates a request for EUR transfer  
2. AIB forwards the request to ESB  
3. ESB sends a clearing statement to AIB  
4. AIB approves or disputes the statement  
5. ESB remits the EUR to the beneficiary 

At first glance, what appears to be a simple, few-second process actually takes   
days – usually two. Normally, the schedule is as follows:

Day 1:
- Client initiates a transfer request  
- AIB forwards the request to ESB

Day 2:
- ESB sends a clearing statement  
- AIB approves or disputes it  
- ESB remits the EUR to the beneficiary 

The process described above holds true only if the days following the initiation of the transfer are business days. Over the weekend, settlement does not take place, therefore, transaction requests submitted by AIB clients after cut-off hours are not forwarded to ESB and will not appear in Monday's clearing statement. This creates the first discrepancy. AIB has debited the client's account but has not yet settled the transaction with ESB. A reconciliation analyst will detect this discrepancy and must be able to identify the nature of the issue and handle it appropriately. A more detailed description of how to resolve these transactions will be covered directly in the specific examples below.

## Exercise assumptions

Each bank structures its SEPA payment settlement process with counterparties differently. Let's define the assumptions under which we will reconcile our synthetic data:

1. The banking system operates from 8 AM to 5 PM
2. Eurozone Settlement Bank charges a fixed fee of €10 per payment processed; no other fees are charged by any bank

## Synthetic Data, Processing Errors and Discrepancies

As you probably realized in the previous chapter, errors or discrepancies can occur in many places throughout this process. While some of them have been eliminated due to automation and reduced human intervention, numerous areas remain where these discrepancies may still arise. I aim to demonstrate these discrepancies using sample data – fictitious transactions presented in their simplest form possible, yet designed to reflect the reality of the issue as accurately as possible.

### Data Structure – Apex International Bank

Dataset `Apex_International_Bank_transactions.csv` contains outgoing transaction data initiated by clients on Friday, June 12, 2026\.  
The file header consists of:

- `tx_id`: A unique transaction identifier within the Apex International Bank system.  
- `date`: The transaction initiation date   
- `time`: The transaction initiation time  
- `sender_acc_number`: The account number of the Apex International Bank client.  
- `beneficiary_iban`: The beneficiary's IBAN (not restricted by region).  
- `amount`: The EUR amount requested for transfer.  
- `fee_type`: The fee disposition code, containing one of the following values: `OUR | SHA | BEN`  
  * `OUR` – Fee is paid by sender; it is settled with AIB off-statement; the beneficiary must receive the full transaction amount  
  * `SHA` – The fee is shared; the sender's fee is settled off-statement, and the beneficiary receives the amount minus any incoming bank fees on their end  
  * `BEN` – The beneficiary pays all fees, which are deducted from the transaction amount en route. The beneficiary receives a reduced net amount, which will also appear on the statement from the correspondent bank  
- `catch`: A flag identifying a "catchy" transaction (one that should be uncovered during the exercise). Consists of 1 (catch) or 0 (normal).

### Data Structure – Eurozone Settlement Bank

Dataset `Eurozone_Settlement_Bank_statement.csv` contains transaction data processed by the counterparty, Eurozone Settlement Bank, on Monday, June 15, 2026\.  
The file header consists of:

- `ext_ref_id`: A unique transaction identifier within the Eurozone Settlement Bank system  
- `date`: The date of settlement  
- `remittance_info`: Settlement details; contains either the unique interbank transaction identifier (UETR) used for matching with AIB, or specific bank code (`CHGS/...`, `INT.CALC/...`, `REV/...`) for transactions initiated directly by the clearing bank  
- `cleared_amount`: The EUR amount settled and charged by Eurozone Settlement Bank to Apex International Bank  
- `catch`: A flag identifying a "catchy" transaction (one that should be uncovered during the exercise). Consists of `1` (catch) or `0` (normal).

### Process Errors

This category encompasses actual system failures or human error on the part of the clearing bank (Eurozone Settlement Bank). These scenarios require manual intervention, the filling of a claim, and, in practice, represent direct financial or reputational risk.

Processing errors are errors which would harm at least one of the parties of contract relationship: AIB, ESB or client of AIB. Harm example might be for example:

* **Missing transaction in the Eurozone Settlement Bank statement** – The AIB client is harmed due to the resulting payment delay  
* **Double processing in the Eurozone Settlement Bank statement** – ESB charges the same transaction twice; harming AIB  
* **Incorrectly calculated `cleared_amount`** – ESB errs in fee calculation, charging AIB higher or lower clearing fees than required  
* …

Such processing errors can take many forms. Typically, they belong to one of two groups:

1. Human error  
2. Automation failure

Nowadays, both groups have been eliminated in nearly 100% of cases – but crucially, only nearly. Anything can happen, and a reconciliation analyst must always be equipped to uncover these issues under all circumstances. Regardless of whether a discrepancy is detected automatically or manually, both approaches require an understanding of the underlying processes and proper calibration of monitoring tools.

### Processing Discrepancies

These scenarios are not errors in the common sense. Instead, they are legitimate procedural phenomena, inherent to banking operations that a reconciliation analyst must be able to identify, separated from actual errors, and properly account for. 

An example for such processing discrepancy is a situation where a client initiates a standard SEPA payment during the evening, specifically after 5:00 PM. Based on our assumptions, the standard banking system does not operate after 5:00 PM, meaning the transaction is held for settlement until the following business day (starting at 8:00 AM). Consequently, these evening transactions remain unposted for a certain period and will only be captured in the next business day's ESB clearing statement. For the purposes of this assignment, this means that transactions initiated after 5:00 PM will appear in the clearing statement that arrives at AIB two days later.

## Simulated Errors

### 1. Double Posting

- **Background:** Technical difficulty on the ESB side results in a single correct client instruction from AIB being cleared more than once. The data are affected as follows: the clearing statement from ESB contains multiple independent rows with unique `ext_ref_id`, but all of them carry the same payment UETR and the same positive amount.

- **Consequence:** If reconciliation software fails to identify this duplicate and approves it, AIB transfers the same funds multiple times, resulting in direct financial loss. Conversely, on the beneficiary's side, unjust enrichment occurs.

### 2. Missing Clearing

- **Background:** Due to technical difficulties (e.g., a communication node failure), ESB fails to include a legitimate instruction in AIB's daily clearing cycle. The transaction exists in AIB internal records but the record is completely missing from the ESB clearing statement.


- **Consequence:** The AIB client's money has been debited from their account (or blocked) but the funds never left the Nostro account for the target bank. This results in an undelivered payment, penalties for delayed processing and a potential dispute filed by the client.

### 3. Error in Fee Charging

-  **Background:** The clearing bank fails to respect the fee disposition instructions (`fee_type`). For **OUR**\-type transactions (sender pays) and **SHA**\-type (shared fees), the cleared amount should equal the nominal transaction value. If the ESB incorrectly applies the rules for the **BEN**\-type (fee paid by the beneficiary), it deducts the SEPA fee directly from the amount being transferred.

 

- **Data impact:** Since amounts in statements are always positive, this error appears as lower `cleared_amount` in the ESB statement than the amount recorded by AIB. The difference matches the bank fee exactly.


- **Consequence:** The beneficiary receives less money than intended, resulting in a loss for the client, or the loss must be compensated by AIB from its revenues as part of the dispute resolution process.

### 4. Amount Mismatch

- **Background:** Human error during manual data entry or system glitch (e.g., an incorrect currency conversion) on the ESB side results in a transaction being cleared for a completely incorrect amount – a variance that cannot be explained even by fee differences.

- **Data impact:** Both sides share the same UETR reference, but the amount in AIB’s internal system does not match the `cleared_amount` in the ESB statement.

- **Consequence:** Asymmetric risk. If the clearing bank clears a higher amount, more funds leave AIB’s Nostro account than the client requested (resulting in loss for AIB). Conversely, if ESB clears a lower amount, fewer funds are transferred resulting in leaving the transaction incomplete (resulting in a loss for ESB, which must cover the shortfall from its own resources).

### 5. Misrouted Transactions

- **Background:** The clearing bank’s system encounters a transaction-pairing or routing error, resulting in transactions belonging to another bank's Nostro account being mistakenly included in AIB’s clearing statement.

- **Data impact:** The ESB statement contains records that include a client UETR reference within the `remittance_info` field, but this UETR does not match any transaction recorded in AIB’s internal system.

- **Consequence**: If AIB approves such a transaction, it would settle a payment that was never initiated by its own client. Because no funds can be debited from an AIB account the bank would have to fund the transfer entirely from its own resources, resulting in a direct financial loss.

## Simulated processing discrepancies

### 1. Missing clearing of transaction after 5 PM

- **Background:**Every clearing system operates with a specific cut-off time, which in our scenario is set at 5:00 PM. Although transactions initiated by clients after this threshold are immediately processed internally by AIB, the clearing bank will only include them in the next business day’s statement, in line with standard logic of interbank clearing.


- **Data impact:** During daily reconciliation, the transaction appears as “missing from the Eurozone Settlement Bank statement” (i.e., it exists in the AIB’s records but is absent from the ESB statement).

- **Consequence:** This is not an error. The reconciliation software must be able to identify these transactions based on their initiation timestamp (5 PM \- 11:59 PM), automatically move them to a transit/suspense account and flag them as “Outstanding Items”. This results in a temporary open balance remaining on the transit account until the next statement arrives. 

### 2. Bank-Initiated Entries

- **Background:** Rows with positive amounts appear in the ESB clearing statement for which no corresponding client instruction (UETR reference) exists within AIB’s systems. In practice, these transactions are initiated by the clearing bank itself. They typically represent regular Nostro account maintenance fees, credited interest, or prior-period reversals.

- **Data impact:** The ESB statement contains records that lack a client reference (UETR) in the `remittance_info` field, displaying specific bank system codes (e.g., `CHGS/...`, `INT.CALC/...`, `REV/...`). There is no counter-operation within the AIB system.  
  * **`CHGS/PERIODIC/MAINTENANCE FEE MAY 2026`**: The clearing bank charges a fee for account maintenance in May 2026\.  
  * **`INT.CALC/CREDIT INTEREST BASE VALUE`**: The clearing bank credits interest for maintaining a positive balance on the Nostro account.  
  * **`SEPA SETTLEMENT ADJUSTMENT NOTE`**: Clearing adjustments for minor technical (rounding) or exchange rate differences that occurred during the day  
  * **`TRF FROM BNP BANK SA / CUSTOMER UNKNOWN`**: An unidentified incoming transfer from another institution (BNP Bank). Funds were credited to the Nostro account, but the payment message lacks a valid identifier or target account number for the AIB beneficiary. These funds must be manually investigated and assigned.

 

- **Consequence:** If the reconciliation software blindly approves such an item as a standard payment, the bank would suffer a financial loss (in the case of fees) or report unallocated income (in the case of interest), both of which constitute a serious breach of accounting standards. Instead of flagging an error, the system must analyze the message string and automatically route these items appropriately: charging fees to bank expenses, routing interest to bank revenues, and forwarding unidentified transactions to the back-office for manual investigation.

## Exercise Output

### Part 1: Validation and Data Preparation

Using SQL, find all the errors and processing discrepancies detailed above. Add a column named “tag” to both tables to classify the transaction status based on the following matrix:

| Tag | Description |
| ----- | ----- |
| MATCHED | The transaction is fully reconciled and correct; AIB approves the match |
| ERR\_DOUBLE\_POSTING | The transaction has been cleared more than once (duplicate posting) |
| ERR\_MISROUTED\_TRANSACTION | The ESB statement contains a transaction that is completely missing from AIB’s internal system |
| ERR\_FEE\_MISMATCH | The ESB statement reflects an error in fee charging (incorrect fee type application) |
| ERR\_MISSING\_BOOKING | The transaction was initiated by AIB but was not cleared by ESB |
| ERR\_AMOUNT\_MISMATCH | The transaction exhibits an amount mismatch between the two systems |
| OUTSTANDING\_ITEM | The transaction was not cleared due to the cut-off time, as expected. It is scheduled to settle on the following business day |
| UNIDENTIFIED\_CUSTOMER | The transaction lacks valid remittance information. The beneficiary cannot be automatically identified, requiring manual investigation to allocate the funds |
| EXPENSE | The transaction represents a direct bank expense (e.g., Nostro account maintenance fees paid by AIB) |
| REVENUE | The transaction represents direct bank revenue (e.g., credit interest credited to AIB). |

### Part 2: Quantifying the Impact

Using SQL,quantify the potential impact on the balance sheet of Apex International Bank in a scenario where all statement items were blindly approved. Answer the following analytical questions:

1) How much money would AIB lose as a direct result of double-posted transactions?  
2) How much funds would AIB mistakenly spend for transactions that were never initiated by its own clients?  
3) How much more in incorrect fees would AIB be charged if transactions were approved as received?  
4) How much money would remain frozen (unsettled) due to the clearing omission on the ESB side?  
5) What is the total volume increase of funds currently held in AIB’s transit (suspense) account as outstanding items?  
6) How much money failed to be automatically credited to internal clients due to missing or unknown beneficiary information?  
7) What is the total absolute volume of transactions initiated by the ESB?

### Part 3: Daily Overview

Using SQL, prepare the data for the bank management's daily report. Management requires insights into the following metrics:

1) What is the total monetary volume of transactions initiated by clients on Friday?  
2) What are the top three destination countries by total monetary volume transferred?  
3) What are the top five destination countries by transaction count (number of payments)?  
4) In which time window were clients most active when initiating payments?  
   * Morning \[6:00-8:30\]  
   * Mid-morning (8:30-11:30\]  
   * Noon \[11:30-13:30\]  
   * Afternoon (13:30-17:00)  
   * Evening \[17:00-20:00\]  
   * Night  
5) What percentage and total volume of Friday-initiated payments were successfully settled?  
6) What is the total volume of transactions from today's ESB statement that was not approved by the reconciliation department? Legitimate bank-operations initiated by the ESB should be considered approved and excluded from this error volume.

### Part 4: Daily Management Overview in Excel

Export the aggregated data from Part 3 into Excel and build a functional, visually polished, and highly informative management dashboard. 

* Develop/record a VBA macro that automatically applies this corporate formatting and style to the raw data. Assign this macro to the keyboard shortcut   
  `CTRL + SHIFT + R`.   
* The finalized .xlsx file will serve as the standardized data attachment sent to AIB management alongside the daily report.

### Part 5: Executive Management Report in Word

Based on the insights and figures gathered across all previous sections, draft an executive summary report for AIB management. 

* The report must be strictly limited to a single A4 page.   
* Provide a high-level, factual interpretation of the critical outcomes from today's reconciliation. Avoid overwhelming management with low-level technical IT details.   
* You must explicitly quantify the identified operational issues, estimate the potential financial exposure (damages prevented), and outline the remediation steps (how the errors are being handled and resolved).
