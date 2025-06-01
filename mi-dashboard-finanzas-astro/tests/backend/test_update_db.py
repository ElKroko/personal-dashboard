import sqlite3

# Connect to the database
conn = sqlite3.connect('data/finanzas.db')
cursor = conn.cursor()

# Update some transactions to be uncategorized for testing
cursor.execute("UPDATE transacciones SET categoria = 'Sin categorizar' WHERE id IN (703, 704, 705)")
conn.commit()

# Verify the update
cursor.execute("SELECT id, detalle, categoria FROM transacciones WHERE id IN (703, 704, 705)")
results = cursor.fetchall()
for row in results:
    print(f"ID: {row[0]}, Detalle: {row[1]}, Categoria: {row[2]}")

conn.close()
print("Updated transactions to uncategorized for testing")
