import pandas as pd
import numpy as np
import random

def generate_grid_data(n_feeders=100, days=30):
    data = []
    states = ['Maharashtra', 'Uttar Pradesh', 'Rajasthan', 
              'Gujarat', 'Bihar', 'Tamil Nadu', 'West Bengal', 
              'Madhya Pradesh']
    
    for i in range(n_feeders):
        for day in range(days):
            units_injected = random.uniform(500, 5000)
            loss_pct = random.uniform(5, 35)
            units_billed = units_injected * (1 - loss_pct / 100)

            record = {
                'feeder_id': f'FEEDER_{i:03d}',
                'state': random.choice(states),
                'date': pd.Timestamp('2024-01-01') + pd.Timedelta(days=day),
                'units_injected_kwh': round(units_injected, 2),
                'units_billed_kwh': round(units_billed, 2),
                'loss_percentage': round(loss_pct, 2),
                'transformer_age_years': random.randint(1, 30),
                'temperature_celsius': round(random.uniform(15, 45), 1),
                'load_factor': round(random.uniform(0.4, 0.95), 2),
                'smart_meter_installed': random.choice([True, False]),
                'voltage_fluctuation': round(random.uniform(0.5, 10.0), 2),
                'outage_hours_monthly': round(random.uniform(0, 20), 1),
            }
            data.append(record)

    df = pd.DataFrame(data)
    df.to_csv('grid_data.csv', index=False)
    print(f"✅ Generated {len(df)} records")
    return df

if __name__ == "__main__":
    generate_grid_data()
