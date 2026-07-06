# Nostro Reconciliation Case Study & Data Generator

> A real world case-study of interbank Nostro account reconciliation including Python synthetic data generator.

## At a Glance (TL;DR) 

* **Format:** A 5-part case study covering SQL, Excel, VBA, Business Reporting  
* **Repository content:**  
  - **The python script** that generates realistic, systematically “dirty” financial data  
  - **Complete assignment briefs** (available in both CZ and EN) simulating real-world business edge cases and explaining all the necessary concepts you need to complete the assignment.  
* **Target Audience:** Aspiring data and reconciliation analysts, finance students, or anyone looking to learn or practice SQL and Excel using data that simulates actual banking operations.  
* **Tech stack:** `Python` (data generation), `SQL` (analysis and transaction matching), `Excel / VBA` (automation and reporting)

## Assignment Structure

The assignment consists of five parts, each focusing on a specific phase of the Nostro statement reconciliation process.

* **Part 1: Data Tagging (SQL):** Cleaning and tagging transactions using predefined error tags  
* **Part 2: Financial Impact (SQL):** Quantifying financial risks and exposure from unapproved items  
* **Part 3: Business Questions (SQL):** Providing a comprehensive overview, statistics, and error rate evaluation  
* **Part 4: Reporting automation (Excel/VBA):** Creating a macro for professional report formatting  
* **Part 5: Executive Summary (Word):** Translating results into concise business insights for the bank's management

## How to start

* Download the prepared SQLite database or generate fresh data running the `Nostro\_reconciliation\_prepare\_data.py`   
* Open the assignment brief located in the `Assignment/` folder  
* You are all set – happy coding\!

## My Motivation – Long Story

For years, I’ve been doing what I love. I am a programmer, and that is something no one can take away from me. In this field, we have to constantly learn and improve. Otherwise, we quickly become irrelevant, and no decent company will look our way. While studying banking at university, I noticed that other financial sectors lag even further behind when it comes to integrating technology. What good is a modern banker who doesn't even know the basics of SQL? After joining the Market Risk department at a bank, I found out the answer – they are of no use. Everyone in my team knows SQL, and at least half of them use Python daily. It is the exact same story in other departments.

When my girlfriend decided she wanted to work in financial controlling and reconciliation, she had never written a single line of SQL or Python code. Yet, the job postings for these roles stated it clearly: SQL is mandatory, Python is a huge advantage. You can probably imagine the shock and disillusionment for someone who deeply understands banking theory but has no programming background.

I built this project for someone who has never seen SQL in their entire life and couldn’t wrap their head around what actual reconciliation looks like from start to finish. I truly believe that the gap between banking theory and real-world practice is a problem we have to start solving ourselves. 

In closing, I would like to note that before starting work on this project, I had no idea what the word “reconciliation” even meant in banking practice (while it might be obvious to native English speakers, it certainly wasn't to me as a native Czech speaker). However, my motivation to empower somebody who deeply understands the theory but lacks a technical background was strong enough to drive me forward. The result is this case study you are going to dive into.

Beyond demonstrating that programmers can (and should) understand the underlying business logic, this project also shows that someone who has never written a single line of code can end up writing plenty of them and become a massive asset to the team..

Wish you the best of luck, success in your career, and happiness in your personal life.  
**Matouš**