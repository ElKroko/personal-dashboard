import pandas as pd
from datetime import datetime, timedelta
import random

# Create sample financial data
start_date = datetime(2024, 1, 1)
end_date = datetime(2024, 12, 31)

# Generate sample transactions
transactions = []
current_date = start_date

# Categories with typical amounts
categories = {
    'Salario': [2500, 3000, 3500],  # Income
    'Freelance': [200, 500, 800],   # Income
    'Alimentación': [-50, -100, -150],  # Expenses
    'Transporte': [-20, -40, -60],      # Expenses
    'Vivienda': [-800, -1000, -1200],   # Expenses
    'Entretenimiento': [-30, -80, -120], # Expenses
    'Salud': [-50, -200, -300],         # Expenses
    'Compras': [-100, -300, -500],      # Expenses
    'Ahorros': [-200, -500, -1000],     # Savings
}

descriptions = {
    'Salario': ['Salario mensual', 'Nómina empresa', 'Pago trabajo'],
    'Freelance': ['Proyecto web', 'Consultoría', 'Trabajo extra'],
    'Alimentación': ['Supermercado Mercadona', 'Restaurante El Rincón', 'Cafetería Central'],
    'Transporte': ['Gasolina BP', 'Metro Madrid', 'Taxi'],
    'Vivienda': ['Alquiler piso', 'Factura luz', 'Factura agua'],
    'Entretenimiento': ['Cinema ABC', 'Spotify', 'Netflix'],
    'Salud': ['Farmacia Cruz Verde', 'Médico privado', 'Dentista'],
    'Compras': ['Amazon', 'Zara', 'El Corte Inglés'],
    'Ahorros': ['Transferencia ahorro', 'Cuenta ahorro', 'Inversión'],
}

# Generate transactions for the year
while current_date <= end_date:
    # Add salary on the 1st of each month
    if current_date.day == 1:
        amount = random.choice(categories['Salario'])
        desc = random.choice(descriptions['Salario'])
        transactions.append({
            'Fecha': current_date,
            'Descripcion': desc,
            'Monto': amount,
            'Categoria': 'Salario'
        })
    
    # Add random transactions (1-3 per day)
    num_transactions = random.choice([0, 1, 1, 2, 3])
    
    for _ in range(num_transactions):
        category = random.choice(list(categories.keys()))
        if category == 'Salario':  # Skip salary (already added monthly)
            continue
            
        amount = random.choice(categories[category])
        desc = random.choice(descriptions[category])
        
        # Add some randomness to amounts
        variation = random.uniform(0.8, 1.2)
        amount = round(amount * variation, 2)
        
        transactions.append({
            'Fecha': current_date,
            'Descripcion': desc,
            'Monto': amount,
            'Categoria': category
        })
    
    current_date += timedelta(days=1)

# Create DataFrame
df = pd.DataFrame(transactions)

# Sort by date
df = df.sort_values('Fecha')

# Format date for Excel
df['Fecha'] = df['Fecha'].dt.strftime('%Y-%m-%d')

# Save to Excel
df.to_excel('sample_transactions.xlsx', index=False)

print(f"Sample Excel file created with {len(df)} transactions")
print(f"Date range: {df['Fecha'].min()} to {df['Fecha'].max()}")
print(f"Total income: {df[df['Monto'] > 0]['Monto'].sum():.2f}")
print(f"Total expenses: {df[df['Monto'] < 0]['Monto'].sum():.2f}")
print(f"Balance: {df['Monto'].sum():.2f}")
