#!/usr/bin/env python3
"""
Script para verificar e instalar dependencias del proyecto
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Ejecutar comando y mostrar resultado"""
    print(f"\n🔄 {description}")
    print(f"Comando: {command}")
    print("-" * 50)
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Éxito!")
            if result.stdout:
                print(f"Output: {result.stdout}")
        else:
            print("❌ Error!")
            if result.stderr:
                print(f"Error: {result.stderr}")
            if result.stdout:
                print(f"Output: {result.stdout}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

def check_python_version():
    """Verificar versión de Python"""
    print(f"🐍 Python version: {sys.version}")
    
    version_info = sys.version_info
    if version_info.major >= 3 and version_info.minor >= 8:
        print("✅ Versión de Python compatible")
        return True
    else:
        print("❌ Se requiere Python 3.8 o superior")
        return False

def install_backend_deps():
    """Instalar dependencias del backend"""
    backend_dir = "backend"
    
    if not os.path.exists(backend_dir):
        print(f"❌ Directorio {backend_dir} no encontrado")
        return False
    
    os.chdir(backend_dir)
    
    # Verificar si existe requirements.txt
    if not os.path.exists("requirements.txt"):
        print("❌ archivo requirements.txt no encontrado")
        return False
    
    # Mostrar contenido de requirements.txt
    print("\n📋 Dependencias a instalar:")
    with open("requirements.txt", "r") as f:
        for line in f:
            print(f"   - {line.strip()}")
    
    # Instalar dependencias
    success = run_command(
        "pip install -r requirements.txt",
        "Instalando dependencias de Python"
    )
    
    os.chdir("..")
    return success

def install_frontend_deps():
    """Instalar dependencias del frontend"""
    frontend_dir = "frontend"
    
    if not os.path.exists(frontend_dir):
        print(f"❌ Directorio {frontend_dir} no encontrado")
        return False
    
    os.chdir(frontend_dir)
    
    # Verificar si existe package.json
    if not os.path.exists("package.json"):
        print("❌ archivo package.json no encontrado")
        return False
    
    # Instalar dependencias
    success = run_command(
        "npm install",
        "Instalando dependencias de Node.js"
    )
    
    os.chdir("..")
    return success

def verify_installation():
    """Verificar que las dependencias estén instaladas"""
    print("\n🔍 VERIFICANDO INSTALACIÓN")
    print("=" * 50)
    
    # Test imports de Python
    python_packages = [
        'fastapi',
        'uvicorn', 
        'pandas',
        'openpyxl',
        'sqlalchemy'
    ]
    
    for package in python_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NO INSTALADO")
    
    # Test comando uvicorn
    result = subprocess.run("uvicorn --version", shell=True, capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ uvicorn - {result.stdout.strip()}")
    else:
        print("❌ uvicorn - comando no disponible")

def create_run_scripts():
    """Crear scripts para ejecutar el proyecto"""
    
    # Script para backend
    backend_script = '''@echo off
echo 🚀 Iniciando backend del Dashboard Financiero...
cd backend
python app.py
pause
'''
    
    with open("run_backend.bat", "w") as f:
        f.write(backend_script)
    
    # Script para frontend  
    frontend_script = '''@echo off
echo 🚀 Iniciando frontend del Dashboard Financiero...
cd frontend
npm run dev
pause
'''
    
    with open("run_frontend.bat", "w") as f:
        f.write(frontend_script)
    
    # Script para tests
    test_script = '''@echo off
echo 🧪 Ejecutando tests del Dashboard Financiero...
python test_debug_errors.py
pause
'''
    
    with open("run_tests.bat", "w") as f:
        f.write(test_script)
    
    print("\n📝 Scripts de ejecución creados:")
    print("   - run_backend.bat  (para iniciar el servidor)")
    print("   - run_frontend.bat (para iniciar la interfaz)")
    print("   - run_tests.bat    (para ejecutar tests)")

def main():
    print("🔧 INSTALADOR Y VERIFICADOR DE DEPENDENCIAS")
    print("Dashboard Financiero Personal")
    print("=" * 60)
    
    # Verificar Python
    if not check_python_version():
        return
    
    # Instalar dependencias del backend
    backend_ok = install_backend_deps()
    
    # Instalar dependencias del frontend
    frontend_ok = install_frontend_deps()
    
    # Verificar instalación
    if backend_ok:
        verify_installation()
    
    # Crear scripts de ejecución
    create_run_scripts()
    
    # Resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE INSTALACIÓN")
    print("=" * 60)
    print(f"🐍 Python:     ✅ Compatible")
    print(f"🔧 Backend:    {'✅ Instalado' if backend_ok else '❌ Error'}")
    print(f"🌐 Frontend:   {'✅ Instalado' if frontend_ok else '❌ Error'}")
    
    if backend_ok and frontend_ok:
        print("\n🎉 ¡Instalación completada con éxito!")
        print("\n📚 Próximos pasos:")
        print("1. Ejecutar: run_backend.bat   (en una consola)")
        print("2. Ejecutar: run_frontend.bat  (en otra consola)")
        print("3. Abrir: http://localhost:4321")
        print("4. Para tests: run_tests.bat")
    else:
        print("\n⚠️ Hubo problemas en la instalación.")
        print("Revisa los errores arriba y ejecuta el script nuevamente.")

if __name__ == "__main__":
    main()
