# Prueba simple para ver lecturas crudas
import adafruit_dht
import board
import time

sensor = adafruit_dht.DHT11(board.D4)

print("Leyendo 20 veces...")
for i in range(20):
    try:
        temp = sensor.temperature
        humidity = sensor.humidity
        print(f"{i+1}. Temp: {temp}°C, Humedad: {humidity}%")
    except RuntimeError as e:
        print(f"{i+1}. Error: {e}")
    time.sleep(3)

sensor.exit()
