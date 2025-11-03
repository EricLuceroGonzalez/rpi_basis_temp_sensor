import time
import board
import adafruit_dht

# Inicializar el sensor DHT11 en el pin GPIO4 (pin 7 físico)
# Cambia board.D4 por el pin que estés usando (D4, D17, D18, etc.)
dhtDevice = adafruit_dht.DHT22(board.D17)

print("Probando sensor DHT11...")
print("Presiona Ctrl+C para salir\n")

try:
    while True:
        try:
            # Leer temperatura y humedad
            temperature = dhtDevice.temperature
            humidity = dhtDevice.humidity
            
            # Imprimir los valores
            print(f"Temperatura: {temperature}°C")
            print(f"Humedad: {humidity}%")
            print("-" * 40)
            
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
