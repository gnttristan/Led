import machine
import neopixel
import time

LED_COUNT = 300
LED_PIN = 0

np = neopixel.NeoPixel(machine.Pin(LED_PIN), LED_COUNT)

print(LED_COUNT)
for i in range(LED_COUNT):
    np[i] = (100, 0, 0)  # (R, G, B)

print("red")
