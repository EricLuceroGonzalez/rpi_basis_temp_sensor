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

app = Flask(__name__)
CORS(app)

# Configurar sensor
dhtDevice = adafruit_dht.DHT22(board.D17)

# Variables globales
current_temp = None
current_humidity = None
last_update = None

# Inicializar base de datos
def init_db():
    """Crear tabla si no existe"""
    conn = sqlite3.connect('dht22_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS readings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT NOT NULL,
                  temperature REAL NOT NULL,
                  humidity REAL NOT NULL)''')
    conn.commit()
    conn.close()
    print("Base de datos inicializada")

def save_reading(temp, humidity):
    """Guardar lectura en base de datos"""
    try:
        conn = sqlite3.connect('dht22_data.db')
        c = conn.cursor()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute("INSERT INTO readings (timestamp, temperature, humidity) VALUES (?, ?, ?)",
                  (timestamp, temp, humidity))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error guardando en BD: {e}")

def get_recent_readings(limit=500):
    """Obtener últimas N lecturas"""
    try:
        conn = sqlite3.connect('dht22_data.db')
        c = conn.cursor()
        c.execute("SELECT timestamp, temperature, humidity FROM readings ORDER BY id DESC LIMIT ?", (limit,))
        rows = c.fetchall()
        conn.close()
        # Invertir para tener orden cronológico
        return list(reversed(rows))
    except Exception as e:
        print(f"Error leyendo BD: {e}")
        return []

def read_sensor():
    """Lee el sensor continuamente y guarda en BD"""
    global current_temp, current_humidity, last_update
    
    while True:
        try:
            temp = dhtDevice.temperature
            humidity = dhtDevice.humidity
            
            if temp is not None and humidity is not None:
                current_temp = temp
                current_humidity = humidity
                last_update = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Guardar en base de datos
                save_reading(temp, humidity)
                
                print(f"✓ Guardado: {temp}°C, {humidity}% - {last_update}")
                
        except RuntimeError as error:
            print(f"Error de lectura: {error.args[0]}")
        except Exception as e:
            print(f"Error inesperado: {e}")
        
        time.sleep(30.0)  # Guardar cada 30 segundos

# Inicializar BD
init_db()

# Iniciar lectura en hilo separado
sensor_thread = threading.Thread(target=read_sensor, daemon=True)
sensor_thread.start()

@app.route('/')
def index():
    """Página principal"""
    return render_template('index.html')

@app.route('/api/current')
def get_current():
    """API: Datos actuales"""
    return jsonify({
        'temperature': current_temp,
        'humidity': current_humidity,
        'timestamp': last_update
    })

@app.route('/api/history')
def get_history():
    """API: Histórico de datos"""
    readings = get_recent_readings(2500)
    
    timestamps = [r[0] for r in readings]
    temperatures = [r[1] for r in readings]
    humidities = [r[2] for r in readings]
    
    return jsonify({
        'timestamps': timestamps,
        'temperature': temperatures,
        'humidity': humidities,
        'total_readings': len(readings)
    })

@app.route('/api/stats')
def get_stats():
    """API: Estadísticas"""
    readings = get_recent_readings(2500)  # Últimas lecturas
    
    if not readings:
        return jsonify({'error': 'No hay datos'})
    
    temps = [r[1] for r in readings]
    hums = [r[2] for r in readings]
    
    return jsonify({
        'temperature': {
            'current': current_temp,
            'min': min(temps),
            'max': max(temps),
            'avg': sum(temps) / len(temps)
        },
        'humidity': {
            'current': current_humidity,
            'min': min(hums),
            'max': max(hums),
            'avg': sum(hums) / len(hums)
        },
        'total_readings': len(readings)
    })
    
@app.route('/api/total_count')
def get_total_count():
    """API: Total de registros en la base de datos"""
    try:
        conn = sqlite3.connect('dht22_data.db')
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM readings")
        total = c.fetchone()[0]
        
        # Obtener fecha del primer y último registro
        c.execute("SELECT MIN(timestamp), MAX(timestamp) FROM readings")
        first, last = c.fetchone()
        
        conn.close()
        
        return jsonify({
            'total_readings': total,
            'first_reading': first,
            'last_reading': last
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500    

@app.route('/download/csv')
def download_csv():
    """Descargar datos como CSV"""
    readings = get_recent_readings(10000)  # Últimas 10000 lecturas
    
    # Crear CSV en memoria
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'Temperature (°C)', 'Humidity (%)'])
    
    for row in readings:
        writer.writerow(row)
    
    # Preparar respuesta
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode()),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'sensor_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    )

@app.route('/api/clear_data')
def clear_data():
    """Limpiar todos los datos (usar con cuidado)"""
    try:
        conn = sqlite3.connect('dht22_data.db')
        c = conn.cursor()
        c.execute("DELETE FROM readings")
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Datos eliminados'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("=" * 60)
    print("🌡️  Servidor DHT11 con Plotly y SQLite iniciado")
    print("=" * 60)
    print("📊 Accede a: http://0.0.0.0:5000")
    print("💾 Base de datos: sensor_data.db")
    print("📥 Descargar CSV: http://0.0.0.0:5000/download/csv")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=False)
