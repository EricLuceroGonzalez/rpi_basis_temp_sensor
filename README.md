# 🌡️ Monitor de Temperatura y Humedad DHT11

Sistema de monitoreo en tiempo real con Raspberry Pi y sensor DHT11. Incluye interfaz web con gráficos interactivos usando Plotly y almacenamiento en base de datos SQLite.

![Status](https://img.shields.io/badge/Status-Active-success)
![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-3%2F4%2F5-red)
![DHT11](https://img.shields.io/badge/Sensor-DHT11-orange)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue)

## 📋 Características

- ✅ Lectura continua de temperatura y humedad
- 📊 Gráficos interactivos en tiempo real con Plotly
- 💾 Almacenamiento permanente en SQLite
- 📥 Exportación de datos a CSV
- 🌐 Acceso desde navegador web
- 📱 Interfaz responsive (móvil y desktop)
- 📈 Estadísticas: mínimo, máximo y promedio

## 🛠️ Hardware Requerido

- Raspberry Pi (cualquier modelo con GPIO)
- Sensor DHT11
- Cables jumper
- Resistencia pull-up 10kΩ (opcional, algunos módulos la incluyen)

## 🔌 Conexión del Hardware

```
DHT11        Raspberry Pi
------------------------
VCC    →     Pin 1 (3.3V) o Pin 2 (5V)
DATA   →     Pin 7 (GPIO4)
GND    →     Pin 6 (GND)
```

## 📦 Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/dht11-monitor.git
cd dht11-monitor
```

### 2. Instalar dependencias del sistema

```bash
sudo apt-get update
sudo apt-get install python3-dev python3-pip libgpiod2
```

### 3. Instalar librerías Python

```bash
pip install flask flask-cors adafruit-circuitpython-dht plotly
```

### 4. Crear estructura de carpetas

```bash
mkdir templates
```

## 🚀 Uso

### Ejecución simple

```bash
python3 app.py
```

Accede a: `http://localhost:5000`

### Ejecución en segundo plano con Screen

```bash
# Iniciar sesión screen
screen -S dht11

# Ejecutar aplicación
python3 app.py

# Desconectar (Ctrl+A, luego D)
# Reconectar: screen -r dht11
```

## 🌐 Acceso Remoto

### Desde la misma red WiFi

```bash
# Obtener IP de la Raspberry
hostname -I

# Acceder desde otro dispositivo
http://192.168.X.X:5000
```

### Desde Internet (usando Tailscale)

```bash
# Instalar Tailscale
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up

# Acceder usando la IP de Tailscale desde cualquier lugar
```

## 📊 API Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Interfaz web principal |
| `/api/current` | GET | Datos actuales del sensor |
| `/api/history` | GET | Histórico de lecturas (últimas 100) |
| `/api/stats` | GET | Estadísticas (min, max, avg) |
| `/download/csv` | GET | Descargar datos en formato CSV |

### Ejemplos de uso de la API

```bash
# Obtener lectura actual
curl http://localhost:5000/api/current

# Obtener histórico
curl http://localhost:5000/api/history

# Obtener estadísticas
curl http://localhost:5000/api/stats
```

## 📁 Estructura del Proyecto

```
dht11-monitor/
├── app.py                 # Aplicación Flask principal
├── templates/
│   └── index.html        # Interfaz web con Plotly
├── sensor_data.db        # Base de datos SQLite (se crea automáticamente)
├── README.md
└── requirements.txt
```

## 🐛 Solución de Problemas

### Error: "GPIO busy"

```bash
# Matar procesos Python
pkill -f python3

# O detener sesión screen
screen -X -S dht11 quit
```

### Error: "Python.h: No such file or directory"

```bash
sudo apt-get install python3-dev
```

### Sensor siempre marca 20°C

- Verifica las conexiones
- Prueba otro pin GPIO
- Revisa el voltaje (3.3V o 5V)
- El sensor puede estar defectuoso

### Cambiar pin GPIO

Edita en `app.py`:

```python
# Cambiar board.D4 por el GPIO que uses
dhtDevice = adafruit_dht.DHT11(board.D4)
```

Pines disponibles: `D4`, `D17`, `D27`, `D22`, `D23`, `D24`

## 🔧 Configuración

### Cambiar intervalo de lectura

En `app.py`, modifica:

```python
time.sleep(5.0)  # Cambiar a los segundos deseados
```

### Cambiar puerto del servidor

```python
app.run(host='0.0.0.0', port=5000)  # Cambiar 5000 por otro puerto
```

## 📝 Base de Datos

Los datos se guardan en `sensor_data.db` con la siguiente estructura:

```sql
CREATE TABLE readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    temperature REAL NOT NULL,
    humidity REAL NOT NULL
)
```

Consultar datos manualmente:

```bash
sqlite3 sensor_data.db "SELECT * FROM readings ORDER BY id DESC LIMIT 10;"
```

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👤 Autor

**Tu Nombre**
- GitHub: [@tu-usuario](https://github.com/tu-usuario)
- Email: tu-email@ejemplo.com

## 🙏 Agradecimientos

- [Adafruit](https://www.adafruit.com/) por las librerías de sensores
- [Plotly](https://plotly.com/) por los gráficos interactivos
- [Flask](https://flask.palletsprojects.com/) por el framework web

## 📚 Referencias

- [Documentación DHT11](https://www.adafruit.com/product/386)
- [Pinout Raspberry Pi](https://pinout.xyz/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Plotly Python](https://plotly.com/python/)

---

⭐ Si este proyecto te fue útil, dale una estrella en GitHub!
