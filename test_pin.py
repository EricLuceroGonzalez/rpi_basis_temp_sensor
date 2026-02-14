# Prueba simple para ver lecturas crudas
import adafruit_dht
import board
import time

try:
    sensor = adafruit_dht.DHT22(board.D17)
    print("Sensor conectado en pin 17")
except RuntimeError as e:
    print(f"Error: {e}")

print("Leyendo 20 veces...")
for i in range(20):
    print(f"i = {i+1}")
    try:
        temp = sensor.temperature
        humidity = sensor.humidity
        print(f"{i+1}. Temp: {temp}°C, Humedad: {humidity}%")
    except RuntimeError as e:
        print(f"{i+1}. Error: {e}")
    time.sleep(3)

sensor.exit()
