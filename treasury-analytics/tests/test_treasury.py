import copy
import json
import unittest
from treasury import ROOT, cash_position, forecast, reconcile, unique_rows


class TreasuryControls(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'data' / 'synthetic_case.json').read_text())

    def test_known_closing_cash_and_restricted_cash(self):
        cash = cash_position(self.data)
        self.assertEqual(cash['bank_usd_cents'], 21508000)
        self.assertEqual(cash['available_usd_cents'], 20508000)
        self.assertEqual(cash['operational_cash_usd_cents'], 24508000)

    def test_exception_bridge_equals_account_balance_difference(self):
        rec = reconcile(self.data['bank'], self.data['ledger'])
        self.assertEqual(len(rec['matched']), 4)
        self.assertEqual(len(rec['exceptions']), 5)
        self.assertEqual(rec['duplicate_bank_ids'], ['B002'])
        for a in cash_position(self.data)['accounts']:
            bridge = sum(e['difference_cents'] for e in rec['exceptions'] if e['account'] == a['account'])
            self.assertEqual(bridge, a['unreconciled_difference_cents'])

    def test_conflicting_duplicate_rejected(self):
        row = copy.deepcopy(self.data['bank'][0])
        row['amount_cents'] += 1
        with self.assertRaises(ValueError):
            unique_rows([self.data['bank'][0], row])

    def test_ambiguous_reference_never_auto_matches(self):
        row = copy.deepcopy(self.data['bank'][0])
        row['id'] = 'NEW_ID'
        rec = reconcile(self.data['bank'] + [row], self.data['ledger'])
        self.assertTrue(any(e['status'] == 'ambiguous_reference' for e in rec['exceptions']))
        self.assertEqual(len(rec['matched']), 3)

    def test_currency_and_account_prevent_cross_matching(self):
        bank = [self.data['bank'][0]]
        ledger = [dict(self.data['ledger'][0], currency='EUR')]
        self.assertEqual(len(reconcile(bank, ledger)['matched']), 0)

    def test_date_review_and_future_cutoff(self):
        bank, ledger = [self.data['bank'][0]], [dict(self.data['ledger'][0], date='2026-11-01')]
        self.assertEqual(reconcile(bank, ledger)['exceptions'][0]['status'], 'date_review')
        data = copy.deepcopy(self.data)
        data['bank'][0]['date'] = '2026-12-01'
        with self.assertRaises(ValueError):
            cash_position(data)

    def test_roll_forward_and_horizon_consistency(self):
        rows = forecast(20508000, self.data['weekly_schedule'], 7500000)
        short = forecast(20508000, self.data['weekly_schedule'][:13], 7500000)
        self.assertEqual(rows[:13], short)
        for i, row in enumerate(rows):
            self.assertEqual(row['closing_cents'], row['opening_cents'] + row['receipts_cents'] - row['payments_cents'])
            if i:
                self.assertEqual(row['opening_cents'], rows[i-1]['closing_cents'])

    def test_stress_delays_receipts_without_inventing_inflow(self):
        rows = forecast(20508000, self.data['weekly_schedule'], 7500000, '0.90', '1.08', 1)
        self.assertEqual(rows[0]['receipts_cents'], 0)
        self.assertEqual(rows[1]['receipts_cents'], self.data['weekly_schedule'][0]['receipts_cents'] * 9 // 10)
        self.assertTrue(any(r['below_buffer'] for r in rows))


if __name__ == '__main__':
    unittest.main()
