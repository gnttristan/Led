import machine
import neopixel
import time
import sys

LED_COUNT = 300
LED_PIN = 0

np = neopixel.NeoPixel(machine.Pin(LED_PIN), LED_COUNT)

BYTES_PER_FRAME = LED_COUNT * 3

for i in range(LED_COUNT):
    np[i] = (100, 0, 0)
    np.write()

while True:
    data = sys.stdin.buffer.read(BYTES_PER_FRAME)
    if data and len(data) == BYTES_PER_FRAME:
        # Convert each 3 bytes → RGB tuple
        for i in range(LED_COUNT):
            r = data[i*3]
            g = data[i*3 + 1]
            b = data[i*3 + 2]
            np[i] = (r, g, b)
        np.write()
        time.sleep(0.1)



