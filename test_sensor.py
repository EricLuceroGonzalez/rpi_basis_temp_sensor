import time
import board
import adafruit_dht
import adafruit_as7341 
# Inicializar el sensor DHT11 en el pin GPIO4 (pin 7 físico)
# Cambia board.D4 por el pin que estés usando (D4, D17, D18, etc.)
try:
    dhtDevice = adafruit_dht.DHT22(board.D17)
    print("DHT_22 encontrado")
    print(dhtDevice.temperature)
except Exception as e:
    print("Error al inicializar DHT_22")
    print(f"Error: {e}")
# --- Configuración del Sensor AS7341 ---
try:
    # 2. INICIALIZAR EL BUS I2C
    i2c = board.I2C()  # Esto usa automáticamente SDA (GPIO 2) y SCL (GPIO 3)
    
    # 3. INICIALIZAR EL SENSOR
    as7341 = adafruit_as7341.AS7341(i2c)
    print("Sensor AS7341 encontrado.")
except Exception as e:
    print(f"Error al inicializar AS7341 (¿Habilitaste I2C?): {e}")
    as7341 = None # Ponerlo en None para que el bucle no falle
print("Probando sensor DHT11...")
print("Presiona Ctrl+C para salir\n")

try:
    while True:
        try:
            # Leer temperatura y humedad
            temperature = dhtDevice.temperature
            humidity = dhtDevice.humidity
            # Leer colores de 8 canales de color principales
            violeta = as7341.channel_415nm
            indigo = as7341.channel_445nm
            azul = as7341.channel_480nm
            cyan = as7341.channel_515nm
            verde = as7341.channel_555nm
            amarillo = as7341.channel_590nm
            naranja = as7341.channel_630nm
            rojo = as7341.channel_680nm
            
            # Imprimir los valores
            print(f"Temperatura: {temperature}°C")
            print(f"Humedad: {humidity}%")
            print("-" * 40)
            
            print(f"Violeta: {violeta}, Indigo: {indigo}, Azul: {azul}")
            print(f"Cyan: {cyan}, Verde: {verde}, amarillo: {amarillo}")
            print(f"Naranja: {naranja}, Rojo: {rojo}")
        except RuntimeError as error:
            # Los errores de lectura son comunes con el DHT11
            print(f"Error de lectura: {error.args[0]}")
            time.sleep(2.0)
            continue
        except Exception as error:
            dhtDevice.exit()
            raise error
        
        # Esperar 2 segundos entre lecturas (el DHT11 es lento)
        time.sleep(2.0)

except KeyboardInterrupt:
    print("\nPrograma terminado")
    dhtDevice.exit()
