-- Execute against reports/treasury_demo.sqlite after running treasury.py.
-- Balances are integer cents; division by 100.0 presents USD.
SELECT scenario, MIN(week) AS first_week_below_buffer
FROM forecast WHERE buffer_gap_cents > 0 GROUP BY scenario;

SELECT scenario, week, start_date, closing_cents / 100.0 AS closing_usd,
       buffer_gap_cents / 100.0 AS buffer_gap_usd
FROM forecast WHERE week IN (13, 26) ORDER BY scenario, week;

-- Control query: expected result is zero rows.
SELECT * FROM forecast
WHERE opening_cents + receipts_cents - payments_cents <> closing_cents;
