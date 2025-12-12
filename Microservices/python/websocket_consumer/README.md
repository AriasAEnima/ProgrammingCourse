# 📥 WebSocket Consumer - Cliente de Notificaciones de Muebles

Cliente WebSocket que escucha y muestra en tiempo real las notificaciones sobre operaciones con muebles (creación, modificación, eliminación).

## 🚀 Instalación

```bash
pip install -r requirements.txt
```

## ▶️ Ejecutar

Primero asegúrate de que el servidor WebSocket esté corriendo, luego:

```bash
python websocket_consumer.py
```

## 📺 Ejemplo de Salida

```
🎯 Consumidor de Notificaciones de Muebles
==================================================
🚀 Iniciando consumidor de notificaciones de muebles...
📍 Conectando a: ws://localhost:8765
⏹️  Para detener: Ctrl+C
--------------------------------------------------
✅ Conectado al servidor WebSocket

[14:30:15] 🔗 Conectado al servidor de notificaciones de muebles
👥 Clientes conectados: 1
------------------------------

[14:30:45] 🪑 Nuevo mueble creado: Mesa de Roble - roble (120x75cm)
   🆔 ID: 673a2f1b8e4d2a1c3b5e6f7a
   🏷️  Nombre: Mesa de Roble
   📏 Dimensiones: 120cm (ancho) x 75cm (alto)
   🪵 Material: roble
   👤 Autor: Juan
   🎉 ¡Nuevo mueble disponible en el catálogo!
------------------------------

[14:31:10] 🪑 Mueble actualizado: Mesa de Roble XL - 150x80cm
   🆔 ID: 673a2f1b8e4d2a1c3b5e6f7a
   🏷️  Nombre: Mesa de Roble XL
   📏 Dimensiones: 150cm (ancho) x 80cm (alto)
   🪵 Material: pino
   👤 Autor: Juan
   🔄 Información del mueble actualizada
------------------------------

[14:32:00] 🪑 Mueble eliminado: Mesa de Roble XL
   🆔 ID: 673a2f1b8e4d2a1c3b5e6f7a
   🏷️  Nombre: Mesa de Roble XL
   📏 Dimensiones: 150cm (ancho) x 80cm (alto)
   🪵 Material: pino
   👤 Autor: Juan
   🗑️  Mueble eliminado del catálogo
------------------------------
```

## 🔌 Conexión

- **Por defecto:** `ws://localhost:8765`
- **Personalizar:** Usa variable de entorno `WEBSOCKET_URL` o modifica el parámetro en el constructor

```bash
# Usando variable de entorno
export WEBSOCKET_URL=ws://otro-servidor:8765
python websocket_consumer.py
```

## 🛑 Detener

Presiona `Ctrl+C` para detener el consumidor.

