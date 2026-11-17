"""Treasury case study. Synthetic inputs only; Python 3.10+, standard library."""
from __future__ import annotations

import json
import sqlite3
from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def scaled(cents: int, factor: str) -> int:
    return int((Decimal(cents) * Decimal(factor)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))


def unique_rows(rows: list[dict]) -> tuple[list[dict], list[str]]:
    """Ignore identical repeated source IDs, but reject conflicting versions."""
    seen, duplicates = {}, []
    for row in rows:
        key = row['id']
        if key in seen:
            if row != seen[key]:
                raise ValueError(f'Conflicting duplicate source ID: {key}')
            duplicates.append(key)
        else:
            if type(row['amount_cents']) is not int:
                raise ValueError('Amounts must be integer cents')
            date.fromisoformat(row['date'])
            seen[key] = row
    return list(seen.values()), duplicates


def reconcile(bank: list[dict], ledger: list[dict]) -> dict:
    """Match account + currency + reference, only for unambiguous one-to-one pairs.

    Exact amounts and a maximum three-day date difference are required. Differences
    remain review items; the engine never creates or posts accounting adjustments.
    """
    bank, duplicates_bank = unique_rows(bank)
    ledger, duplicates_ledger = unique_rows(ledger)
    groups = defaultdict(lambda: {'bank': [], 'ledger': []})
    for side, rows in [('bank', bank), ('ledger', ledger)]:
        for row in rows:
            groups[(row['account'], row['currency'], row['reference'])][side].append(row)
    matched, exceptions = [], []
    for key, group in sorted(groups.items()):
        b, l = group['bank'], group['ledger']
        item = {'account': key[0], 'currency': key[1], 'reference': key[2],
                'bank_ids': [r['id'] for r in b], 'ledger_ids': [r['id'] for r in l],
                'bank_cents': sum(r['amount_cents'] for r in b),
                'ledger_cents': sum(r['amount_cents'] for r in l)}
        if len(b) > 1 or len(l) > 1:
            item['status'] = 'ambiguous_reference'
        elif b and l:
            lag = abs((date.fromisoformat(b[0]['date']) - date.fromisoformat(l[0]['date'])).days)
            if b[0]['amount_cents'] != l[0]['amount_cents']:
                item['status'] = 'amount_difference'
            elif lag > 3:
                item['status'] = 'date_review'
            else:
                matched.append(item)
                continue
        else:
            item['status'] = 'bank_only' if b else 'ledger_only'
        item['difference_cents'] = item['bank_cents'] - item['ledger_cents']
        exceptions.append(item)
    return {'matched': matched, 'exceptions': exceptions,
            'duplicate_bank_ids': duplicates_bank, 'duplicate_ledger_ids': duplicates_ledger,
            'unique_bank_rows': len(bank), 'unique_ledger_rows': len(ledger)}


def cash_position(data: dict) -> dict:
    bank, _ = unique_rows(data['bank'])
    ledger, _ = unique_rows(data['ledger'])
    cutoff = date.fromisoformat(data['as_of'])
    accounts = {a['id']: a for a in data['accounts']}
    for row in bank + ledger:
        if row['account'] not in accounts or row['currency'] != accounts[row['account']]['currency']:
            raise ValueError('Unknown account or currency mismatch')
        if date.fromisoformat(row['date']) > cutoff:
            raise ValueError('Transaction falls after reporting date')
    result = []
    for account in data['accounts']:
        closing = account['opening_bank_cents'] + sum(r['amount_cents'] for r in bank if r['account'] == account['id'])
        book = account['opening_ledger_cents'] + sum(r['amount_cents'] for r in ledger if r['account'] == account['id'])
        restricted = account['restricted_cents']
        if restricted < 0 or restricted > closing:
            raise ValueError('Invalid restricted balance')
        fx = data['fx_usd_per_unit'][account['currency']]
        result.append({'account': account['id'], 'currency': account['currency'],
                       'bank_cents': closing, 'ledger_cents': book,
                       'unreconciled_difference_cents': closing - book,
                       'bank_usd_cents': scaled(closing, fx),
                       'restricted_usd_cents': scaled(restricted, fx),
                       'available_usd_cents': scaled(closing - restricted, fx)})
    bank_total = sum(r['bank_usd_cents'] for r in result)
    available = sum(r['available_usd_cents'] for r in result)
    return {'accounts': result, 'bank_usd_cents': bank_total,
            'available_usd_cents': available,
            'restricted_usd_cents': bank_total - available,
            'kiosk_usd_cents': data['kiosk_usd_cents'],
            'transit_usd_cents': data['transit_usd_cents'],
            'operational_cash_usd_cents': bank_total + data['kiosk_usd_cents'] + data['transit_usd_cents']}


def forecast(opening: int, schedule: list[dict], floor: int, receipt_factor='1',
             payment_factor='1', delay_weeks=0) -> list[dict]:
    if type(delay_weeks) is not int or delay_weeks < 0:
        raise ValueError('delay_weeks must be a non-negative integer')
    if Decimal(receipt_factor) < 0 or Decimal(payment_factor) < 0:
        raise ValueError('Scenario factors must be non-negative')
    rows, balance = [], opening
    for i, week in enumerate(schedule):
        source = i - delay_weeks
        receipts = scaled(schedule[source]['receipts_cents'], receipt_factor) if source >= 0 else 0
        payments = scaled(week['payments_cents'], payment_factor)
        closing = balance + receipts - payments
        rows.append({'week': i + 1, 'start_date': week['start_date'], 'opening_cents': balance,
                     'receipts_cents': receipts, 'payments_cents': payments, 'closing_cents': closing,
                     'buffer_gap_cents': max(0, floor - closing), 'below_buffer': closing < floor})
        balance = closing
    return rows


def money(cents: int) -> str:
    return f'{Decimal(cents) / 100:,.2f}'


def write_report(data: dict, result: dict) -> None:
    cash, rec = result['cash_position'], result['reconciliation']
    base, stress = result['forecast_base'], result['forecast_stress']
    def first_breach(rows):
        return next((str(r['week']) for r in rows if r['below_buffer']), 'None')
    lines = ['# Treasury review pack', '', '**Independent case study | Synthetic data | USD reporting currency**', '',
             f"Reporting date: {data['as_of']}. FX rates are fixed illustrative assumptions, not market quotes.", '',
             '## Daily cash position', '', '| Metric | USD |', '|---|---:|',
             f"| Bank cash | {money(cash['bank_usd_cents'])} |",
             f"| Restricted cash | {money(cash['restricted_usd_cents'])} |",
             f"| Available bank cash | {money(cash['available_usd_cents'])} |",
             f"| Kiosk cash | {money(cash['kiosk_usd_cents'])} |",
             f"| Cash in transit | {money(cash['transit_usd_cents'])} |",
             f"| Total operational cash | {money(cash['operational_cash_usd_cents'])} |", '',
             'Kiosk and transit balances are separate custodial buckets. Neither is included in available bank cash. '
             'The USD 6,000 ledger deposit is part of the USD 12,000 transit bucket; it is not added twice. '
             'Transfers between buckets do not generate revenue or external cash inflow.', '',
             '## Bank reconciliation', '',
             f"{len(rec['matched'])} exact pairs; {len(rec['exceptions'])} exception groups; "
             f"{len(rec['duplicate_bank_ids'])} identical bank-source duplicate excluded.", '',
             'Match rate uses unique bank lines: '
             f"{len(rec['matched'])}/{rec['unique_bank_rows']} = {len(rec['matched']) / rec['unique_bank_rows']:.1%}.", '',
             '| Account | Currency | Bank closing | Ledger closing | Bank less ledger |', '|---|---|---:|---:|---:|']
    for a in cash['accounts']:
        lines.append(f"| {a['account']} | {a['currency']} | {money(a['bank_cents'])} | {money(a['ledger_cents'])} | {money(a['unreconciled_difference_cents'])} |")
    lines += ['', '| Reference | Status | Bank less ledger | Currency | Suggested review |', '|---|---|---:|---|---|']
    actions = {'bank_only': 'Request bank advice; verify classification before proposing a journal',
               'ledger_only': 'Verify settlement date and supporting evidence',
               'amount_difference': 'Compare payment instruction, invoice and bank advice',
               'ambiguous_reference': 'Resolve duplicate references manually', 'date_review': 'Review value date and period cutoff'}
    for e in rec['exceptions']:
        lines.append(f"| {e['reference']} | {e['status']} | {money(e['difference_cents'])} | {e['currency']} | {actions[e['status']]} |")
    lines += ['', 'The sum of exception differences explains each account balance difference because opening bank and '
              'ledger balances agree in this sample. This is an arithmetic bridge, not approval to post journals. '
              'The USD 7,000 unidentified receipt remains unresolved and provisionally sits in available bank cash; '
              'treasury must assess whether to quarantine it. Account sign-off remains open.', '',
              '## Liquidity forecast', '',
              'Both horizons use the same 26-week schedule: the 13-week view is its first 13 rows. '
              'Opening balance is available bank cash. EUR cash is translated at 1.10 USD/EUR; '
              'this assumes convertibility and free transfer, without FX costs. Weekly flows are external flows in USD equivalents.', '',
              'Base: receipts and payments as scheduled. Stress: receipts 10% lower and delayed by one week, '
              'payments 8% higher. No opening overdue receivable is assumed in the stress case; the final delayed receipt '
              'falls beyond the forecast horizon and is not silently moved back.', '',
              f"Illustrative minimum buffer: USD {money(data['buffer_usd_cents'])}.", '',
              '| Scenario | Week 13 closing USD | Week 26 closing USD | First week below buffer |', '|---|---:|---:|---|',
              f"| Base | {money(base[12]['closing_cents'])} | {money(base[25]['closing_cents'])} | {first_breach(base)} |",
              f"| Stress | {money(stress[12]['closing_cents'])} | {money(stress[25]['closing_cents'])} | {first_breach(stress)} |", '',
              '### Management discussion', '',
              'Review the planned week-6 equipment payment and week-18 tax payment against the buffer. '
              'Discuss timing with the business, validate collection dates and escalate any funding gap for management review. '
              'Do not assume a new credit line, delayed supplier payment or automatic FX conversion is approved.', '',
              '### Weekly detail', '',
              '| Week | Start | Base receipts | Base payments | Base close | Stress close | Stress buffer gap |', '|---|---|---:|---:|---:|---:|---:|']
    for b, s in zip(base, stress):
        lines.append(f"| {b['week']} | {b['start_date']} | {money(b['receipts_cents'])} | {money(b['payments_cents'])} | {money(b['closing_cents'])} | {money(s['closing_cents'])} | {money(s['buffer_gap_cents'])} |")
    lines += ['', '## Scope', '', 'This portfolio exercise does not connect to banks, an ERP or a TMS. It does not claim NetSuite, '
              'Kyriba, FIS, ION or IFRS compliance. It does not model digital-asset custody, token valuation, bank cut-off times, '
              'intraday liquidity or legal restrictions by entity. All exception resolution and journal posting require human review.', '']
    (ROOT / 'reports' / 'treasury_review.md').write_text('\n'.join(lines), encoding='utf-8')


def write_svg(data: dict, result: dict) -> None:
    """Self-contained repository preview, no external fonts or scripts."""
    cash = result['cash_position']
    base, stress = result['forecast_base'], result['forecast_stress']
    values = [r['closing_cents'] / 100 for r in base + stress] + [data['buffer_usd_cents'] / 100, 0]
    lo, hi = min(values) - 25000, max(values) + 25000
    x = lambda i: 90 + i * 1020 / 25
    y = lambda v: 540 - (v - lo) / (hi - lo) * 270
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="690" viewBox="0 0 1200 690">',
             '<rect width="1200" height="690" fill="#f3f6fa"/>',
             '<rect width="1200" height="145" fill="#102a43"/>',
             '<g font-family="Arial, sans-serif"><text x="52" y="48" font-size="14" letter-spacing="3" fill="#85d5c8">JESUS COLBERT REANO / TREASURY ANALYTICS</text>',
             '<text x="52" y="96" font-size="35" font-weight="700" fill="white">Cash visibility. Exceptions. Liquidity.</text>',
             f'<text x="52" y="124" font-size="14" fill="#c8d6e5">Independent case study | Synthetic data | As of {data["as_of"]}</text>']
    cards = [('AVAILABLE BANK CASH', '$' + money(cash['available_usd_cents'])),
             ('RECONCILIATION EXCEPTIONS', str(len(result['reconciliation']['exceptions']))),
             ('FORECAST HORIZONS', '13 / 26 weeks')]
    for i, (label, value) in enumerate(cards):
        xx = 52 + i * 374
        parts += [f'<rect x="{xx}" y="167" width="348" height="80" rx="7" fill="white"/>',
                  f'<text x="{xx+20}" y="192" font-size="12" fill="#526779">{label}</text>',
                  f'<text x="{xx+20}" y="226" font-size="28" font-weight="700" fill="#102a43">{value}</text>']
    for tick in range(5):
        v = lo + (hi-lo)*tick/4
        yy = y(v)
        parts += [f'<line x1="90" y1="{yy:.1f}" x2="1110" y2="{yy:.1f}" stroke="#dbe3ec"/>',
                  f'<text x="76" y="{yy+4:.1f}" text-anchor="end" font-size="12" fill="#62788b">{v/1000:.0f}k</text>']
    floor_y = y(data['buffer_usd_cents'] / 100)
    parts.append(f'<line x1="90" y1="{floor_y:.1f}" x2="1110" y2="{floor_y:.1f}" stroke="#8191a0" stroke-dasharray="7 5"/>')
    for series, color in [(base, '#008474'), (stress, '#bc4d37')]:
        points = ' '.join(f'{x(i):.1f},{y(r["closing_cents"]/100):.1f}' for i,r in enumerate(series))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
    for i in [0,5,12,17,25]:
        parts.append(f'<text x="{x(i):.1f}" y="568" text-anchor="middle" font-size="12" fill="#526779">W{i+1}</text>')
    parts += ['<text x="90" y="601" font-size="14" fill="#008474">Base forecast</text>',
              '<text x="270" y="601" font-size="14" fill="#bc4d37">Stress forecast</text>',
              '<text x="470" y="601" font-size="14" fill="#62788b">Dashed line: illustrative $75,000 buffer</text>',
              '<text x="52" y="650" font-size="13" fill="#526779">Python + SQL | Exact matching with review queue | Fixed illustrative FX | All amounts in USD equivalents</text>', '</g></svg>']
    (ROOT / 'reports' / 'treasury_preview.svg').write_text('\n'.join(parts), encoding='utf-8')


def run() -> dict:
    data = json.loads((ROOT / 'data' / 'synthetic_case.json').read_text(encoding='utf-8'))
    cash = cash_position(data)
    rec = reconcile(data['bank'], data['ledger'])
    base = forecast(cash['available_usd_cents'], data['weekly_schedule'], data['buffer_usd_cents'])
    stress = forecast(cash['available_usd_cents'], data['weekly_schedule'], data['buffer_usd_cents'], '0.90', '1.08', 1)
    result = {'as_of': data['as_of'], 'synthetic': True, 'cash_position': cash, 'reconciliation': rec,
              'forecast_base': base, 'forecast_stress': stress}
    reports = ROOT / 'reports'
    reports.mkdir(exist_ok=True)
    (reports / 'results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    with sqlite3.connect(reports / 'treasury_demo.sqlite') as con:
        con.execute('DROP TABLE IF EXISTS forecast')
        con.execute('CREATE TABLE forecast (scenario TEXT, week INTEGER, start_date TEXT, opening_cents INTEGER, receipts_cents INTEGER, payments_cents INTEGER, closing_cents INTEGER, buffer_gap_cents INTEGER, PRIMARY KEY(scenario, week))')
        for scenario, rows in [('base', base), ('stress', stress)]:
            con.executemany('INSERT INTO forecast VALUES (?,?,?,?,?,?,?,?)',
                            [(scenario, r['week'], r['start_date'], r['opening_cents'], r['receipts_cents'], r['payments_cents'], r['closing_cents'], r['buffer_gap_cents']) for r in rows])
    write_report(data, result)
    write_svg(data, result)
    print(f"Available cash USD {money(cash['available_usd_cents'])}; {len(rec['exceptions'])} exceptions; 26-week base and stress forecasts generated.")
    return result


if __name__ == '__main__':
    run()
