from flask import Flask, render_template, jsonify, send_file
from flask_cors import CORS
import adafruit_dht
import board
import threading
import time
from datetime import datetime
import sqlite3
import csv
import io

# --- Nuevas importaciones para el AS7341 ---
import adafruit_as7341

app = Flask(__name__)
CORS(app)

# --- Configurar Sensor 1 (DHT22) ---
try:
    dhtDevice = adafruit_dht.DHT22(board.D17)
except Exception as e:
    print(f"Error al inicializar DHT22: {e}")
    dhtDevice = None

# --- Configurar Sensor 2 (AS7341) ---
try:
    i2c = board.I2C() 
    as7341 = adafruit_as7341.AS7341(i2c)
    print("Sensor AS7341 inicializado con éxito.")
except Exception as e:
    print(f"Error al inicializar AS7341 (¿Habilitaste I2C con raspi-config?): {e}")
    as7341 = None

# Variables globales
current_temp = None
current_humidity = None
current_spectral_data = {} 
last_update = None

# --- Base de Datos (Dos Tablas) ---
DATABASE_FILE = 'sensor_data.db'

def init_db():
    """Crear AMBAS tablas si no existen"""
    conn = sqlite3.connect(DATABASE_FILE)
    c = conn.cursor()
    # Tabla 1: DHT22
    c.execute('''CREATE TABLE IF NOT EXISTS dht_readings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT NOT NULL,
                  temperature REAL,
                  humidity REAL)''')
    # Tabla 2: AS7341
    c.execute('''CREATE TABLE IF NOT EXISTS spectral_readings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT NOT NULL,
                  f415nm REAL, f445nm REAL, f480nm REAL, f515nm REAL,
                  f555nm REAL, f590nm REAL, f630nm REAL, f680nm REAL
                  )''')
    conn.commit()
    conn.close()
    print(f"Base de datos inicializada con 2 tablas: {DATABASE_FILE}")

def save_dht_reading(timestamp, temp, humidity):
    """Guardar lectura de DHT en su tabla"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute("INSERT INTO dht_readings (timestamp, temperature, humidity) VALUES (?, ?, ?)",
                  (timestamp, temp, humidity))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error guardando en BD (DHT): {e}")

def save_spectral_reading(timestamp, spectral_data):
    """Guardar lectura de AS7341 en su tabla"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        s_data = spectral_data or {} # Asegurar que sea un dict
        
        values = (
            timestamp,
            s_data.get('f415nm'), s_data.get('f445nm'), s_data.get('f480nm'), s_data.get('f515nm'),
            s_data.get('f555nm'), s_data.get('f590nm'), s_data.get('f630nm'), s_data.get('f680nm')
        )
        
        c.execute('''INSERT INTO spectral_readings (
                        timestamp, f415nm, f445nm, f480nm, f515nm,
                        f555nm, f590nm, f630nm, f680nm
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', values)
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error guardando en BD (Spectral): {e}")

def get_recent_dht_readings(limit=500):
    """Obtener últimas N lecturas de DHT"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute("SELECT timestamp, temperature, humidity FROM dht_readings ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        return list(reversed(rows))
    except Exception as e:
        print(f"Error leyendo BD (DHT): {e}")
        return []

def get_recent_spectral_readings(limit=500):
    """Obtener últimas N lecturas espectrales"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute('''SELECT timestamp, f415nm, f445nm, f480nm, f515nm,
                        f555nm, f590nm, f630nm, f680nm
                     FROM spectral_readings ORDER BY id DESC LIMIT ?''', (limit,))
        rows = c.fetchall()
        conn.close()
        return list(reversed(rows))
    except Exception as e:
        print(f"Error leyendo BD (Spectral): {e}")
        return []

# --- Hilo de Lectura (Modificado para 2 tablas) ---
def read_sensor():
    """Lee ambos sensores y guarda en tablas separadas"""
    global current_temp, current_humidity, last_update, current_spectral_data
    
    while True:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # --- 1. Leer y Guardar DHT22 ---
        if dhtDevice:
            temp, humidity = None, None
            try:
                temp = dhtDevice.temperature
                humidity = dhtDevice.humidity
                
                if temp is not None and humidity is not None:
                    current_temp = temp
                    current_humidity = humidity
                    save_dht_reading(timestamp, temp, humidity)
                    print(f"✓ Guardado DHT: T={temp}°C, H={humidity}%")
                
            except RuntimeError as error:
                print(f"Error de lectura DHT: {error.args[0]}")
                print(f"Error en tiempo: {timestamp}")
            except Exception as e:
                print(f"Error inesperado DHT: {e}")

        # --- 2. Leer y Guardar AS7341 ---
        if as7341:
            spectral_data = {}
            try:
                spectral_data = {
                    'f415nm': as7341.channel_415nm, 'f445nm': as7341.channel_445nm,
                    'f480nm': as7341.channel_480nm, 'f515nm': as7341.channel_515nm,
                    'f555nm': as7341.channel_555nm, 'f590nm': as7341.channel_590nm,
                    'f630nm': as7341.channel_630nm, 'f680nm': as7341.channel_680nm
                }
                current_spectral_data = spectral_data
                save_spectral_reading(timestamp, spectral_data)
                print(f"✓ Guardado AS7341: V={spectral_data['f415nm']}, R={spectral_data['f680nm']}")
                
            except Exception as e:
                print(f"Error de lectura AS7341: {e}")

        last_update = timestamp
        time.sleep(30.0)

# --- Endpoints de Flask (Actualizados) ---

init_db()
sensor_thread = threading.Thread(target=read_sensor, daemon=True)
sensor_thread.start()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/current')
def get_current():
    """API: Datos actuales (no cambia)"""
    return jsonify({
        'temperature': current_temp,
        'humidity': current_humidity,
        'spectral_data': current_spectral_data,
        'timestamp': last_update
    })

@app.route('/api/history')
def get_history():
    """API: Histórico de datos de ambas tablas"""
    dht_readings = get_recent_dht_readings(2500)
    spectral_readings = get_recent_spectral_readings(2500)
    
    # Empaquetar datos DHT
    dht_data = {
        'timestamps': [r[0] for r in dht_readings],
        'temperature': [r[1] for r in dht_readings],
        'humidity': [r[2] for r in dht_readings]
    }
    
    # Empaquetar datos espectrales
    spectral_data = {
        'timestamps': [r[0] for r in spectral_readings],
        'f415nm': [r[1] for r in spectral_readings], 'f445nm': [r[2] for r in spectral_readings],
        'f480nm': [r[3] for r in spectral_readings], 'f515nm': [r[4] for r in spectral_readings],
        'f555nm': [r[5] for r in spectral_readings], 'f590nm': [r[6] for r in spectral_readings],
        'f630nm': [r[7] for r in spectral_readings], 'f680nm': [r[8] for r in spectral_readings]
    }
    
    return jsonify({
        'dht_history': dht_data,
        'spectral_history': spectral_data,
        'total_dht_readings': len(dht_readings),
        'total_spectral_readings': len(spectral_readings)
    })

def get_stats_for_list(data_list):
    """Función helper para calcular estadísticas filtrando Nones"""
    data_list = [d for d in data_list if d is not None]
    if not data_list:
        return {'min': None, 'max': None, 'avg': None}
    return {
        'min': min(data_list),
        'max': max(data_list),
        'avg': round(sum(data_list) / len(data_list), 2)
    }

@app.route('/api/stats')
def get_stats():
    """API: Estadísticas de ambas tablas"""
    dht_readings = get_recent_dht_readings(2500)
    spectral_readings = get_recent_spectral_readings(2500)
    
    if not dht_readings and not spectral_readings:
        return jsonify({'error': 'No hay datos'})
    
    temps = [r[1] for r in dht_readings]
    hums = [r[2] for r in dht_readings]
    
    stats_response = {
        'temperature': {
            'current': current_temp,
            **get_stats_for_list(temps)
        },
        'humidity': {
            'current': current_humidity,
            **get_stats_for_list(hums)
        },
        'spectral_data': {
            'f415nm': get_stats_for_list([r[1] for r in spectral_readings]),
            'f445nm': get_stats_for_list([r[2] for r in spectral_readings]),
            'f480nm': get_stats_for_list([r[3] for r in spectral_readings]),
            'f515nm': get_stats_for_list([r[4] for r in spectral_readings]),
            'f555nm': get_stats_for_list([r[5] for r in spectral_readings]),
            'f590nm': get_stats_for_list([r[6] for r in spectral_readings]),
            'f630nm': get_stats_for_list([r[7] for r in spectral_readings]),
            'f680nm': get_stats_for_list([r[8] for r in spectral_readings])
        },
        'total_readings_dht': len(dht_readings),
        'total_readings_spectral': len(spectral_readings)
    }
    return jsonify(stats_response)
    
@app.route('/api/total_count')
def get_total_count():
    """API: Total de registros en AMBAS tablas"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM dht_readings")
        total_dht = c.fetchone()[0]
        c.execute("SELECT MIN(timestamp), MAX(timestamp) FROM dht_readings")
        first_dht, last_dht = c.fetchone()
        
        c.execute("SELECT COUNT(*) FROM spectral_readings")
        total_spectral = c.fetchone()[0]
        c.execute("SELECT MIN(timestamp), MAX(timestamp) FROM spectral_readings")
        first_spectral, last_spectral = c.fetchone()
        
        conn.close()
        
        return jsonify({
            'dht_readings': {
                'total_readings': total_dht,
                'first_reading': first_dht,
                'last_reading': last_dht
            },
            'spectral_readings': {
                'total_readings': total_spectral,
                'first_reading': first_spectral,
                'last_reading': last_spectral
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500    

@app.route('/download/dht_csv')
def download_dht_csv():
    """Descargar datos de DHT como CSV"""
    readings = get_recent_dht_readings(10000)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'Temperature (°C)', 'Humidity (%)'])
    
    for row in readings:
        writer.writerow(row)
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'dht_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/download/spectral_csv')
def download_spectral_csv():
    """Descargar datos espectrales como CSV"""
    readings = get_recent_spectral_readings(10000)
    output = io.StringIO()
    writer = csv.writer(output)
    
    header = ['Timestamp', 'f415nm', 'f445nm', 'f480nm', 'f515nm',
              'f555nm', 'f590nm', 'f630nm', 'f680nm']
    writer.writerow(header)
    
    for row in readings:
        writer.writerow(row)
    
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'spectral_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/api/clear_data')
def clear_data():
    """Limpiar todos los datos de AMBAS tablas"""
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM dht_readings")
        c.execute("DELETE FROM spectral_readings")
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Datos de ambas tablas eliminados'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("=" * 60)
    print("🌡️💡 Servidor de Sensores (DHT22 + AS7341) iniciado")
    print("=" * 60)
    print("📊 Accede a: http://0.0.0.0:5000")
    print(f"💾 Base de datos: {DATABASE_FILE}")
    print("📥 Descargar DHT CSV: http://0.0.0.0:5000/download/dht_csv")
    print("📥 Descargar Spectral CSV: http://0.0.0.0:5000/download/spectral_csv")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
