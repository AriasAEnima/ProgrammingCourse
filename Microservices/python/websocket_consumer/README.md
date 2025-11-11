# 📥 WebSocket Consumer - Cliente de Notificaciones de Mesas

Cliente WebSocket que escucha y muestra en tiempo real las notificaciones sobre operaciones con mesas.

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
🎯 Consumidor de Notificaciones de Mesas
==================================================
🚀 Iniciando consumidor de notificaciones de mesas...
📍 Conectando a: ws://localhost:8765
⏹️  Para detener: Ctrl+C
--------------------------------------------------
✅ Conectado al servidor WebSocket

[14:30:15] 🔗 Conectado al servidor de notificaciones de mesas
👥 Clientes conectados: 1
------------------------------

[14:30:45] 🪑 Nueva mesa creada: Mesa Ejecutiva (180x90cm)
   🆔 ID: 673a2f1b8e4d2a1c3b5e6f7a
   🏷️  Nombre: Mesa Ejecutiva
   📏 Dimensiones: 180cm x 90cm
   🎉 ¡Nueva mesa disponible!
------------------------------

[14:31:10] 🪑 Mesa actualizada: Mesa Ejecutiva XL - 200x100cm
   🆔 ID: 673a2f1b8e4d2a1c3b5e6f7a
   🏷️  Nombre: Mesa Ejecutiva XL
   📏 Dimensiones: 200cm x 100cm
   🔄 Mesa modificada
------------------------------
```

## 🔌 Conexión

- **Por defecto:** `ws://localhost:8765`
- **Personalizar:** Edita `websocket_url` en el constructor

## 🛑 Detener

Presiona `Ctrl+C` para detener el consumidor.

