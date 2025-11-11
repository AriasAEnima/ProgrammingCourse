#!/usr/bin/env python3
"""
Script de utilidad para limpiar y organizar logs del sistema WebSocket + Flask
"""

import os
import shutil
import glob

def clean_logs():
    """Limpiar logs mal ubicados y organizar carpeta logs/"""
    
    print("🧹 Limpiando y organizando logs...")
    
    # Crear carpeta logs si no existe
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"📁 Directorio {logs_dir}/ creado")
    
    # Encontrar logs en el directorio principal
    main_dir_logs = glob.glob("*.log")
    
    if main_dir_logs:
        print(f"🔄 Moviendo {len(main_dir_logs)} logs a {logs_dir}/:")
        
        for log_file in main_dir_logs:
            dest_path = os.path.join(logs_dir, log_file)
            
            # Si el archivo ya existe en logs/, hacer backup
            if os.path.exists(dest_path):
                backup_path = f"{dest_path}.backup"
                shutil.move(dest_path, backup_path)
                print(f"   📦 Backup: {log_file} → {log_file}.backup")
            
            # Mover el archivo
            shutil.move(log_file, dest_path)
            print(f"   ➡️  {log_file} → {logs_dir}/{log_file}")
    else:
        print("✅ No hay logs mal ubicados")
    
    # Mostrar contenido de logs/
    if os.path.exists(logs_dir) and os.listdir(logs_dir):
        print(f"\n📋 Contenido de {logs_dir}/:")
        for item in sorted(os.listdir(logs_dir)):
            item_path = os.path.join(logs_dir, item)
            if os.path.isfile(item_path):
                size = os.path.getsize(item_path)
                print(f"   📄 {item} ({size} bytes)")
    else:
        print(f"\n📁 {logs_dir}/ está vacío")
    
    print(f"\n✅ Limpieza completada")
    print(f"💡 Los logs futuros se crearán automáticamente en {logs_dir}/")

def clear_logs():
    """Eliminar todos los logs existentes"""
    
    response = input("⚠️  ¿Eliminar TODOS los logs? (s/N): ").lower().strip()
    
    if response in ['s', 'sí', 'si', 'y', 'yes']:
        logs_dir = "logs"
        
        # Eliminar logs del directorio principal
        main_logs = glob.glob("*.log")
        for log_file in main_logs:
            os.remove(log_file)
            print(f"🗑️  Eliminado: {log_file}")
        
        # Eliminar logs de la carpeta logs/
        if os.path.exists(logs_dir):
            for item in os.listdir(logs_dir):
                if item.endswith('.log'):
                    item_path = os.path.join(logs_dir, item)
                    os.remove(item_path)
                    print(f"🗑️  Eliminado: {logs_dir}/{item}")
        
        print("✅ Todos los logs eliminados")
    else:
        print("❌ Operación cancelada")

def show_logs():
    """Mostrar todos los logs disponibles"""
    
    print("📋 Logs disponibles:")
    print("-" * 40)
    
    logs_dir = "logs"
    found_logs = False
    
    # Logs en directorio principal (mal ubicados)
    main_logs = glob.glob("*.log")
    if main_logs:
        print("⚠️  Logs mal ubicados (directorio principal):")
        for log_file in main_logs:
            size = os.path.getsize(log_file)
            print(f"   📄 {log_file} ({size} bytes)")
        found_logs = True
    
    # Logs en carpeta logs/ (correcto)
    if os.path.exists(logs_dir):
        logs_files = [f for f in os.listdir(logs_dir) if f.endswith('.log')]
        if logs_files:
            print(f"✅ Logs bien organizados ({logs_dir}/):")
            for log_file in sorted(logs_files):
                log_path = os.path.join(logs_dir, log_file)
                size = os.path.getsize(log_path)
                print(f"   📄 {log_file} ({size} bytes)")
            found_logs = True
    
    if not found_logs:
        print("📭 No se encontraron logs")
    
    print(f"\n💡 Para ver logs en tiempo real:")
    print(f"   tail -f {logs_dir}/websocket_consumer.log")
    print(f"   tail -f {logs_dir}/flask_api.log")
    print(f"   tail -f {logs_dir}/websocket_server.log")

def main():
    """Función principal con menú de opciones"""
    
    print("🛠️  Utilidad de Logs - Sistema WebSocket + Flask")
    print("=" * 50)
    print("1. Limpiar y organizar logs")
    print("2. Mostrar logs disponibles")
    print("3. Eliminar todos los logs")
    print("4. Salir")
    print("-" * 50)
    
    try:
        option = input("Selecciona una opción (1-4): ").strip()
        
        if option == "1":
            clean_logs()
        elif option == "2":
            show_logs()
        elif option == "3":
            clear_logs()
        elif option == "4":
            print("👋 ¡Hasta luego!")
        else:
            print("❌ Opción inválida")
            
    except KeyboardInterrupt:
        print("\n👋 ¡Hasta luego!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
