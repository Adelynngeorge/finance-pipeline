import sqlite3
import pandas as pd
from datetime import datetime, timedelta

conn = sqlite3.connect('finance.db')

cc = pd.read_sql("SELECT * FROM credit_cards", conn)
loans = pd.read_sql("SELECT * FROM loans", conn)
conn.close()

cc['type'] = 'Credit Card'
loans['type'] = 'Loan'

all_debts = pd.concat([cc, loans], ignore_index=True)
all_debts['monthly_interest'] = round(all_debts['balance'] * (all_debts['apr'] / 100 / 12), 2)

def simulate(debts, strategy='avalanche', extra=0, lump=0):
    df = debts.copy()
    df['balance'] = df['balance'].astype(float)

    df = df.sort_values('apr', ascending=False).reset_index(drop=True)
    remaining_lump = lump
    for i in df.index:
        if remaining_lump <= 0:
            break
        payment = min(df.at[i, 'balance'], remaining_lump)
        df.at[i, 'balance'] -= payment
        remaining_lump -= payment

    if strategy == 'snowball':
        df = df.sort_values('balance').reset_index(drop=True)
    else:
        df = df.sort_values('apr', ascending=False).reset_index(drop=True)

    month = 0
    total_interest = 0

    while df['balance'].sum() > 0.01 and month < 360:
        month += 1
        freed = 0
        for i in df.index:
            if df.at[i, 'balance'] <= 0:
                continue
            interest = df.at[i, 'balance'] * (df.at[i, 'apr'] / 100 / 12)
            total_interest += interest
            df.at[i, 'balance'] += interest
            pay = min(df.at[i, 'balance'], df.at[i, 'min_payment'])
            df.at[i, 'balance'] -= pay
            if df.at[i, 'balance'] < 0.01:
                freed += df.at[i, 'min_payment']
                df.at[i, 'balance'] = 0

        active = df[df['balance'] > 0].index
        if len(active) > 0:
            df.at[active[0], 'balance'] = max(0, df.at[active[0], 'balance'] - (extra + freed))

    freedom_date = (datetime.today() + timedelta(days=30 * month)).strftime('%Y-%m')
    return {'months': month, 'total_interest': round(total_interest, 2), 'freedom_date': freedom_date}

scenarios = [
    ('avalanche', 0,   0),
    ('snowball',  0,   0),
    ('avalanche', 200, 0),
    ('avalanche', 400, 0),
    ('avalanche', 600, 0),
    ('avalanche', 800, 0),
    ('avalanche', 200, 1000),
]

print("\n--- Debt Summary ---")
print(all_debts[['name', 'type', 'balance', 'apr', 'min_payment', 'monthly_interest']])
print(f"\nTotal Debt:        ${all_debts['balance'].sum():,.2f}")
print(f"Monthly Payments:  ${all_debts['min_payment'].sum():,.2f}")
print(f"Monthly Interest:  ${all_debts['monthly_interest'].sum():,.2f}")

print("\n--- Payoff Simulations ---")
results = []
for strategy, extra, lump in scenarios:
    r = simulate(all_debts, strategy, extra, lump)
    results.append({
        'strategy': strategy,
        'extra_monthly': extra,
        'lump_sum': lump,
        'months_to_free': r['months'],
        'total_interest': r['total_interest'],
        'freedom_date': r['freedom_date']
    })
    print(f"  {strategy:10} +${extra}/mo  +${lump} lump → {r['months']} months | ${r['total_interest']:,.0f} interest | free: {r['freedom_date']}")

all_debts.to_csv('debts_clean.csv', index=False)
pd.DataFrame(results).to_csv('simulations.csv', index=False)
print("\nDone! debts_clean.csv and simulations.csv created.")