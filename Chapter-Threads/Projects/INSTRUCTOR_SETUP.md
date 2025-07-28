# 🎓 INSTRUCTOR SETUP - Proyecto Semanal

**Para Eduardo**: Guía rápida para la semana de proyecto

---

## 📅 **CRONOGRAMA SEMANAL**

```
LUNES:    Session 5 - Distributed Systems (45 min)
MARTES:   DÍA 1 - Threading + Image Processing (45 min seguimiento)
MIÉRCOLES: DÍA 2 - Multiprocessing (45 min seguimiento)  
JUEVES:   DÍA 3 - Distributed + Docker (45 min seguimiento)
VIERNES:  DÍA 4 - CI/CD + Demo Final (45 min seguimiento)
```

---

## 🎯 **PREPARACIÓN CADA DÍA**

### **ANTES DE CADA CLASE (5 min):**
1. Revisar `daily_guides/DAYX_WEEKDAY.md`
2. Verificar que funciona el código base
3. Preparar troubleshooting común

### **DURANTE SEGUIMIENTO (45 min):**
1. **Min 0-10**: Review día anterior + setup
2. **Min 10-40**: Implementación guiada
3. **Min 40-45**: Q&A + tareas autónomas

---

## 🛠️ **ARCHIVOS CLAVE**

### **Plan general:**
- `WEEKLY_PROJECT_PLAN.md` - Overview completo del proyecto

### **Guías diarias:**
- `daily_guides/DAY1_TUESDAY.md` - Threading + Image Processing
- `daily_guides/DAY2_WEDNESDAY.md` - Multiprocessing (TODO)
- `daily_guides/DAY3_THURSDAY.md` - Docker + Distributed (TODO)
- `daily_guides/DAY4_FRIDAY.md` - CI/CD + Demo (TODO)

### **Código base:**
- `image_api/processors.py` - Base threading (DÍA 1)
- `image_api/filters.py` - Filtros de imagen
- `requirements_extended.txt` - Todas las dependencias

---

## 🧪 **TESTING RÁPIDO**

### **Verificar que todo funciona:**
```bash
cd Chapter-Threads/Projects/

# Test código base
python image_api/processors.py
python image_api/filters.py

# Test servidor Django
python manage.py runserver 8000
curl http://localhost:8000/api/image/4k/
```

---

## 🚨 **CONTINGENCIAS COMUNES**

### **Si van retrasados:**
- **DÍA 1**: Solo resize filter + threading básico
- **DÍA 2**: Skip multiprocessing, hacer threading avanzado
- **DÍA 3**: Docker simple, no orchestration
- **DÍA 4**: GitHub Actions básico

### **Si van adelantados:**
- **Extensiones**: ML filters, real-time streaming
- **Optimizaciones**: Caching, GPU acceleration
- **Monitoring**: Grafana dashboards

### **Problemas técnicos típicos:**
- **PIL no instala**: `pip install --upgrade pip`
- **Docker issues**: Usar virtual environments
- **Redis connection**: Usar in-memory queue
- **Threading no speedup**: Verificar I/O-bound tasks

---

## 📊 **EVALUACIÓN DIARIA**

### **Criterios de éxito por día:**

**DÍA 1 (Básico)**: 
- ✅ 2+ filtros funcionando
- ✅ Threading speedup >1.5x

**DÍA 2 (Intermedio)**:
- ✅ Multiprocessing working
- ✅ Performance comparison

**DÍA 3 (Avanzado)**:
- ✅ Docker containers
- ✅ Distributed workers

**DÍA 4 (Profesional)**:
- ✅ CI/CD pipeline
- ✅ Demo presentation

---

## 🎭 **DEMO FINAL - VIERNES**

### **Preparar para presentación (20 min):**
1. **Architecture overview** (5 min)
2. **Live demo** (10 min)
3. **Performance results** (3 min)
4. **Q&A** (2 min)

### **Qué debe funcionar:**
- ✅ Upload imagen → procesamiento distribuido
- ✅ Workers escalando horizontalmente
- ✅ Fault tolerance (worker failure)
- ✅ Monitoring dashboard
- ✅ CI/CD pipeline deployando

---

**🎯 ¡Todo listo para una semana de proyecto epic!** 🚀 