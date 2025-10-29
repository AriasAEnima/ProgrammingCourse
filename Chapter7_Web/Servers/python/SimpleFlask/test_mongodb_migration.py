"""
Script de prueba para verificar la conexión a MongoDB
y la migración de datos desde hardcoded a base de datos
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8003"

def test_login():
    """Probar login con usuarios migrados"""
    print("🧪 Probando login...")
    
    # Probar con admin
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": "admin1",
        "password": "admin123"
    })
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Login exitoso con admin1")
        print(f"   Token: {data['access_token'][:50]}...")
        return data['access_token']
    else:
        print(f"❌ Error en login: {response.text}")
        return None

def test_desks_endpoints(token):
    """Probar endpoints de escritorios"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🧪 Probando GET /desk...")
    response = requests.get(f"{BASE_URL}/desk", headers=headers)
    if response.status_code == 200:
        desks = response.json()
        print(f"✅ GET /desk exitoso - {len(desks)} escritorios encontrados")
        for desk in desks:
            print(f"   - {desk['name']}: {desk['width']}x{desk['height']}")
    else:
        print(f"❌ Error en GET /desk: {response.text}")
    
    print("\n🧪 Probando GET /desk/1...")
    response = requests.get(f"{BASE_URL}/desk/1", headers=headers)
    if response.status_code == 200:
        desk = response.json()
        print(f"✅ GET /desk/1 exitoso - Mesa: {desk['name']}")
    else:
        print(f"❌ Error en GET /desk/1: {response.text}")
    
    print("\n🧪 Probando POST /desk (requiere admin)...")
    new_desk = {
        "name": "Mesa Prueba MongoDB",
        "width": 150,
        "height": 250
    }
    response = requests.post(f"{BASE_URL}/desk", json=new_desk, headers=headers)
    if response.status_code == 201:
        desk = response.json()
        print(f"✅ POST /desk exitoso - Nueva mesa creada: {desk['name']}")
    else:
        print(f"❌ Error en POST /desk: {response.text}")

def main():
    print("🚀 Iniciando pruebas de migración a MongoDB...")
    print("=" * 50)
    
    # Probar login
    token = test_login()
    
    if token:
        # Probar endpoints de escritorios
        test_desks_endpoints(token)
    
    print("\n" + "=" * 50)
    print("🏁 Pruebas completadas")

if __name__ == "__main__":
    main()