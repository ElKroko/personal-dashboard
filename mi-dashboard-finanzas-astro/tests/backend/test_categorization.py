import requests
import json

# Simular lo que hace el frontend
print("=== Prueba de funcionalidad de categorización ===")

# 1. Obtener datos del historial
print("\n1. Obteniendo datos del historial...")
response = requests.get("http://localhost:8000/historial/")
if response.status_code == 200:
    data = response.json()
    print(f"   ✅ Datos obtenidos: {data['total_transacciones']} transacciones")
    
    # Filtrar transacciones sin categorizar (misma lógica que el frontend)
    uncategorized = [
        t for t in data['transacciones'] 
        if not t.get('categoria') or 
           t['categoria'] == 'Sin categorizar' or 
           t['categoria'] == 'Uncategorized' or
           t['categoria'].strip() == ''
    ]
    print(f"   📋 Transacciones sin categorizar: {len(uncategorized)}")
    
    if uncategorized:
        # Tomar la primera transacción sin categorizar
        test_transaction = uncategorized[0]
        print(f"   🎯 Transacción de prueba: ID={test_transaction['id']}, Detalle='{test_transaction['detalle'][:50]}...'")
        
        # 2. Obtener sugerencias para esta transacción
        print(f"\n2. Obteniendo sugerencias para transacción ID {test_transaction['id']}...")
        suggestions_response = requests.post(
            "http://localhost:8000/sugerir-categoria/",
            json={"detalle": test_transaction['detalle']}
        )
        if suggestions_response.status_code == 200:
            suggestions_data = suggestions_response.json()
            print(f"   ✅ Sugerencias obtenidas: {len(suggestions_data['sugerencias'])} sugerencias")
            for i, sugg in enumerate(suggestions_data['sugerencias'][:3]):
                print(f"      {i+1}. {sugg['categoria']} (confianza: {sugg['confianza']:.2f})")
        else:
            print(f"   ❌ Error al obtener sugerencias: {suggestions_response.status_code}")
        
        # 3. Actualizar la categoría
        print(f"\n3. Actualizando categoría de transacción ID {test_transaction['id']}...")
        update_response = requests.patch(
            f"http://localhost:8000/transacciones/{test_transaction['id']}/categoria",
            json={"nueva_categoria": "Gasto - Servicios"}
        )
        if update_response.status_code == 200:
            update_data = update_response.json()
            print(f"   ✅ Categoría actualizada correctamente")
            print(f"      Nueva categoría: {update_data['transaccion']['categoria']}")
            print(f"      Tipo regla: {update_data['transaccion']['tipo_regla']}")
        else:
            print(f"   ❌ Error al actualizar categoría: {update_response.status_code}")
            print(f"      Respuesta: {update_response.text}")
        
        # 4. Verificar que los datos se actualizaron
        print(f"\n4. Verificando actualización...")
        verify_response = requests.get("http://localhost:8000/historial/")
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            new_uncategorized = [
                t for t in verify_data['transacciones'] 
                if not t.get('categoria') or 
                   t['categoria'] == 'Sin categorizar' or 
                   t['categoria'] == 'Uncategorized' or
                   t['categoria'].strip() == ''
            ]
            print(f"   ✅ Transacciones sin categorizar ahora: {len(new_uncategorized)}")
            
            # Buscar la transacción actualizada
            updated_transaction = next((t for t in verify_data['transacciones'] if t['id'] == test_transaction['id']), None)
            if updated_transaction:
                print(f"   ✅ Transacción actualizada encontrada: categoría = '{updated_transaction['categoria']}'")
            else:
                print(f"   ❌ No se encontró la transacción actualizada")
        else:
            print(f"   ❌ Error al verificar actualización: {verify_response.status_code}")
    else:
        print("   ⚠️  No hay transacciones sin categorizar para probar")
else:
    print(f"   ❌ Error al obtener historial: {response.status_code}")

print("\n=== Fin de la prueba ===")
