# ⏰ Session3: Tareas Programadas y Automatización

## 📖 Descripción

Esta sesión cubre la programación y automatización de tareas en sistemas Unix/Linux utilizando diferentes herramientas y técnicas.

## 🎯 Objetivos

- Dominar cron y crontab para tareas periódicas
- Entender systemd timers como alternativa moderna
- Crear scripts de monitoreo y mantenimiento
- Implementar sistemas de automatización robustos
- Manejar logs y notificaciones de tareas

## 📋 Contenido

### 1. Fundamentos de Cron
- Sintaxis de crontab
- Tipos de tareas programadas
- Variables de entorno en cron
- Manejo de salida y errores

### 2. Systemd Timers
- Creación de unidades de servicio
- Configuración de timers
- Ventajas sobre cron tradicional
- Monitoreo con systemctl

### 3. Scripts de Automatización
- Tareas de mantenimiento del sistema
- Respaldos automáticos
- Limpieza de archivos temporales
- Monitoreo de recursos

### 4. Notificaciones y Logging
- Envío de notificaciones por email
- Logging estructurado
- Manejo de errores y alertas
- Integración con herramientas de monitoreo

## 🛠️ Archivos de Práctica

- `01_cron_basics.sh` - Fundamentos de cron y crontab
- `02_systemd_timers.sh` - Gestión de systemd timers
- `03_maintenance_tasks.sh` - Scripts de mantenimiento automático
- `04_monitoring_automation.sh` - Monitoreo y alertas automatizadas

## 🚀 Ejercicios Prácticos

### Ejercicio 1: Configuración de Cron
Crear tareas programadas para:
- Respaldo diario de archivos importantes
- Limpieza semanal de logs antiguos
- Verificación cada hora del espacio en disco

### Ejercicio 2: Systemd Timers
Implementar:
- Timer para actualización de sistema
- Servicio de monitoreo de procesos
- Notificaciones automáticas de estado

### Ejercicio 3: Automatización Completa
Desarrollar:
- Sistema de respaldos inteligente
- Monitor de salud del sistema
- Alertas automáticas por email/webhook

## 📅 Sintaxis de Cron - Referencia Rápida

```
# Formato: MIN HORA DIA MES DIA_SEMANA COMANDO
# 
#   ┌───────────── minutos (0-59)
#   │ ┌─────────── horas (0-23)
#   │ │ ┌───────── día del mes (1-31)
#   │ │ │ ┌─────── mes (1-12)
#   │ │ │ │ ┌───── día de la semana (0-7, 0 y 7 = domingo)
#   │ │ │ │ │
#   * * * * * comando-a-ejecutar

# Ejemplos comunes:
0 2 * * *      # Diario a las 2:00 AM
0 0 * * 0      # Semanal los domingos a medianoche
0 */4 * * *    # Cada 4 horas
*/15 * * * *   # Cada 15 minutos
0 9 1 * *      # El primer día de cada mes a las 9:00 AM
```

## ⚙️ Systemd Timer - Estructura Básica

### Archivo de Servicio (.service)
```ini
[Unit]
Description=Mi tarea automatizada
Wants=mi-tarea.timer

[Service]
Type=oneshot
ExecStart=/ruta/al/script.sh

[Install]
WantedBy=multi-user.target
```

### Archivo de Timer (.timer)
```ini
[Unit]
Description=Timer para mi tarea
Requires=mi-tarea.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

## 🔧 Mejores Prácticas

### Seguridad
- ✅ Usar rutas absolutas en scripts
- ✅ Validar variables de entorno
- ✅ Implementar logging adecuado
- ✅ Manejar permisos correctamente

### Rendimiento
- ✅ Evitar tareas simultáneas pesadas
- ✅ Usar locks para prevenir ejecuciones múltiples
- ✅ Optimizar scripts para uso mínimo de recursos
- ✅ Implementar timeouts apropiados

### Mantenibilidad
- ✅ Documentar todas las tareas programadas
- ✅ Usar nombres descriptivos
- ✅ Centralizar configuración
- ✅ Implementar monitoreo de tareas

## 🐛 Problemas Comunes y Soluciones

### Cron no ejecuta el script
```bash
# Verificar que cron esté corriendo
systemctl status cron

# Revisar logs de cron
tail -f /var/log/cron

# Verificar variables de entorno
env > /tmp/cron-env.txt
```

### Script funciona manual pero no en cron
```bash
# Problema común: PATH diferente
# Solución: Usar rutas absolutas
/usr/bin/python3 /ruta/completa/script.py

# O definir PATH en crontab
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
```

### Systemd timer no se ejecuta
```bash
# Verificar status del timer
systemctl status mi-tarea.timer

# Ver logs del servicio
journalctl -u mi-tarea.service

# Verificar sintaxis del timer
systemd-analyze verify mi-tarea.timer
```

## 📊 Herramientas de Monitoreo

| Herramienta | Uso | Comando |
|-------------|-----|---------|
| `crontab -l` | Listar tareas de cron | `crontab -l` |
| `systemctl list-timers` | Ver timers activos | `systemctl list-timers --all` |
| `journalctl` | Logs de systemd | `journalctl -u servicio.timer` |
| `atq` | Cola de tareas at | `atq` |

## 💡 Recursos Adicionales

- [Cron Guru](https://crontab.guru/) - Generador de expresiones cron
- [Systemd Timers](https://www.freedesktop.org/software/systemd/man/systemd.timer.html) - Documentación oficial
- [Advanced Bash Scripting](https://tldp.org/LDP/abs/html/) - Guía de scripting

---

**Siguiente**: Implementación práctica de sistemas de automatización empresarial
