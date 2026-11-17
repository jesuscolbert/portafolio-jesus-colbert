# Treasury review pack

**Independent case study | Synthetic data | USD reporting currency**

Reporting date: 2026-11-17. FX rates are fixed illustrative assumptions, not market quotes.

## Daily cash position

| Metric | USD |
|---|---:|
| Bank cash | 215,080.00 |
| Restricted cash | 10,000.00 |
| Available bank cash | 205,080.00 |
| Kiosk cash | 18,000.00 |
| Cash in transit | 12,000.00 |
| Total operational cash | 245,080.00 |

Kiosk and transit balances are separate custodial buckets. Neither is included in available bank cash. The USD 6,000 ledger deposit is part of the USD 12,000 transit bucket; it is not added twice. Transfers between buckets do not generate revenue or external cash inflow.

## Bank reconciliation

4 exact pairs; 5 exception groups; 1 identical bank-source duplicate excluded.

Match rate uses unique bank lines: 4/7 = 57.1%.

| Account | Currency | Bank closing | Ledger closing | Bank less ledger |
|---|---|---:|---:|---:|
| US_OPER | USD | 157,880.00 | 149,000.00 | 8,880.00 |
| EU_OPER | EUR | 52,000.00 | 52,100.00 | -100.00 |

| Reference | Status | Bank less ledger | Currency | Suggested review |
|---|---|---:|---|---|
| SUP_EU | amount_difference | -100.00 | EUR | Compare payment instruction, invoice and bank advice |
| BANK_FEE | bank_only | -120.00 | USD | Request bank advice; verify classification before proposing a journal |
| DEPOSIT_IN_TRANSIT | ledger_only | -6,000.00 | USD | Verify settlement date and supporting evidence |
| OUTSTANDING_PAYMENT | ledger_only | 8,000.00 | USD | Verify settlement date and supporting evidence |
| UNIDENTIFIED_RECEIPT | bank_only | 7,000.00 | USD | Request bank advice; verify classification before proposing a journal |

The sum of exception differences explains each account balance difference because opening bank and ledger balances agree in this sample. This is an arithmetic bridge, not approval to post journals. The USD 7,000 unidentified receipt remains unresolved and provisionally sits in available bank cash; treasury must assess whether to quarantine it. Account sign-off remains open.

## Liquidity forecast

Both horizons use the same 26-week schedule: the 13-week view is its first 13 rows. Opening balance is available bank cash. EUR cash is translated at 1.10 USD/EUR; this assumes convertibility and free transfer, without FX costs. Weekly flows are external flows in USD equivalents.

Base: receipts and payments as scheduled. Stress: receipts 10% lower and delayed by one week, payments 8% higher. No opening overdue receivable is assumed in the stress case; the final delayed receipt falls beyond the forecast horizon and is not silently moved back.

Illustrative minimum buffer: USD 75,000.00.

| Scenario | Week 13 closing USD | Week 26 closing USD | First week below buffer |
|---|---:|---:|---|
| Base | 134,080.00 | 161,080.00 | None |
| Stress | -65,460.00 | -181,200.00 | 6 |

### Management discussion

Review the planned week-6 equipment payment and week-18 tax payment against the buffer. Discuss timing with the business, validate collection dates and escalate any funding gap for management review. Do not assume a new credit line, delayed supplier payment or automatic FX conversion is approved.

### Weekly detail

| Week | Start | Base receipts | Base payments | Base close | Stress close | Stress buffer gap |
|---|---|---:|---:|---:|---:|---:|
| 1 | 2026-11-18 | 58,000.00 | 52,000.00 | 211,080.00 | 148,920.00 | 0.00 |
| 2 | 2026-11-25 | 61,000.00 | 52,000.00 | 220,080.00 | 144,960.00 | 0.00 |
| 3 | 2026-12-02 | 64,000.00 | 52,000.00 | 232,080.00 | 143,700.00 | 0.00 |
| 4 | 2026-12-09 | 60,000.00 | 61,000.00 | 231,080.00 | 135,420.00 | 0.00 |
| 5 | 2026-12-16 | 58,000.00 | 52,000.00 | 237,080.00 | 133,260.00 | 0.00 |
| 6 | 2026-12-23 | 61,000.00 | 207,000.00 | 91,080.00 | -38,100.00 | 113,100.00 |
| 7 | 2026-12-30 | 64,000.00 | 52,000.00 | 103,080.00 | -39,360.00 | 114,360.00 |
| 8 | 2027-01-06 | 60,000.00 | 61,000.00 | 102,080.00 | -47,640.00 | 122,640.00 |
| 9 | 2027-01-13 | 58,000.00 | 52,000.00 | 108,080.00 | -49,800.00 | 124,800.00 |
| 10 | 2027-01-20 | 61,000.00 | 52,000.00 | 117,080.00 | -53,760.00 | 128,760.00 |
| 11 | 2027-01-27 | 64,000.00 | 52,000.00 | 129,080.00 | -55,020.00 | 130,020.00 |
| 12 | 2027-02-03 | 60,000.00 | 61,000.00 | 128,080.00 | -63,300.00 | 138,300.00 |
| 13 | 2027-02-10 | 58,000.00 | 52,000.00 | 134,080.00 | -65,460.00 | 140,460.00 |
| 14 | 2027-02-17 | 61,000.00 | 52,000.00 | 143,080.00 | -69,420.00 | 144,420.00 |
| 15 | 2027-02-24 | 64,000.00 | 52,000.00 | 155,080.00 | -70,680.00 | 145,680.00 |
| 16 | 2027-03-03 | 60,000.00 | 61,000.00 | 154,080.00 | -78,960.00 | 153,960.00 |
| 17 | 2027-03-10 | 58,000.00 | 52,000.00 | 160,080.00 | -81,120.00 | 156,120.00 |
| 18 | 2027-03-17 | 61,000.00 | 112,000.00 | 109,080.00 | -149,880.00 | 224,880.00 |
| 19 | 2027-03-24 | 64,000.00 | 52,000.00 | 121,080.00 | -151,140.00 | 226,140.00 |
| 20 | 2027-03-31 | 60,000.00 | 61,000.00 | 120,080.00 | -159,420.00 | 234,420.00 |
| 21 | 2027-04-07 | 58,000.00 | 52,000.00 | 126,080.00 | -161,580.00 | 236,580.00 |
| 22 | 2027-04-14 | 61,000.00 | 52,000.00 | 135,080.00 | -165,540.00 | 240,540.00 |
| 23 | 2027-04-21 | 64,000.00 | 52,000.00 | 147,080.00 | -166,800.00 | 241,800.00 |
| 24 | 2027-04-28 | 60,000.00 | 61,000.00 | 146,080.00 | -175,080.00 | 250,080.00 |
| 25 | 2027-05-05 | 58,000.00 | 52,000.00 | 152,080.00 | -177,240.00 | 252,240.00 |
| 26 | 2027-05-12 | 61,000.00 | 52,000.00 | 161,080.00 | -181,200.00 | 256,200.00 |

## Scope

This portfolio exercise does not connect to banks, an ERP or a TMS. It does not claim NetSuite, Kyriba, FIS, ION or IFRS compliance. It does not model digital-asset custody, token valuation, bank cut-off times, intraday liquidity or legal restrictions by entity. All exception resolution and journal posting require human review.
