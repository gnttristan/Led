import machine
import neopixel
import time

LED_COUNT = 300
LED_PIN = 0

np = neopixel.NeoPixel(machine.Pin(LED_PIN), LED_COUNT)

while True:
    for i in range(LED_COUNT):
        np[i] = (255, 0, 0)  # (R, G, B)

    print("red")

    time.sleep(1)

    for i in range(LED_COUNT):
        np[i] = (0, 0, 0)  # (R, G, B)

    print("white")

    time.sleep(1)
