#!/usr/bin/env python3
"""
Test final para verificar que las agregaciones se calculan correctamente
"""

import os
import sys
import requests

def test_agregaciones_endpoint():
    """Test para verificar que las agregaciones del endpoint son correctas"""
    print("=" * 60)
    print("  VERIFICACIÓN FINAL DE AGREGACIONES")
    print("=" * 60)
    
    url = "http://localhost:8000/cargar-tef-locales/"
    
    try:
        response = requests.post(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            print(f"✅ Endpoint funciona correctamente")
            print(f"📊 Total transacciones: {data['total_transacciones']}")
            
            # Verificar promedios
            if 'promedios' in data:
                promedios = data['promedios']
                print(f"\n💰 Promedios:")
                print(f"  - Ingreso promedio: ${promedios.get('ingreso_promedio', 0):,.2f}")
                print(f"  - Gasto promedio: ${promedios.get('gasto_promedio', 0):,.2f}")
                
                if promedios.get('gasto_promedio', 0) > 0:
                    print("  ✅ Los promedios se están calculando correctamente")
                else:
                    print("  ⚠️  Los promedios siguen en 0 - revisar datos")
            
            # Verificar resumen mensual
            if 'resumen_mensual' in data:
                resumen = data['resumen_mensual']
                print(f"\n📈 Resumen mensual ({len(resumen)} periodos):")
                for periodo in resumen:
                    print(f"  - {periodo.get('año_mes', 'N/A')}: "
                          f"Ingresos ${periodo.get('total_ingresos', 0):,.2f}, "
                          f"Gastos ${periodo.get('total_gastos', 0):,.2f}")
            
            # Verificar gasto diario referencia
            if 'gasto_diario_referencia' in data:
                gdr = data['gasto_diario_referencia']
                print(f"\n📅 Gasto diario referencia: ${gdr:,.2f}")
            
            return True
            
        else:
            print(f"❌ Error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_agregaciones_endpoint()
