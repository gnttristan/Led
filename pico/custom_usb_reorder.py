import machine
import neopixel
import sys
import time
import math

LED_COUNT = 300
LED_PIN = 0
PACKET_SIZE = 64
BYTES_PER_FRAME = PACKET_SIZE * int(math.ceil((LED_COUNT * 3) / PACKET_SIZE))


def reorder(data):
    byte_arrays = []
    for i in range(int(len(data) / PACKET_SIZE)):
        byte_arrays.append((data[i * PACKET_SIZE], data[i * PACKET_SIZE + 1: (i + 1) * PACKET_SIZE]))

    sorted_byte_arrays = list(dict(sorted(byte_arrays, key=lambda b: b[0])).values())
    flattenned_byte_arrays = [x for y in sorted_byte_arrays for x in y][:LED_COUNT * 3]
    return flattenned_byte_arrays


np = neopixel.NeoPixel(machine.Pin(LED_PIN), LED_COUNT)

# Initialize LEDs
for i in range(LED_COUNT):
    np[i] = (0, 1, 0)
np.write()

while True:
    input_data = sys.stdin.buffer.read(BYTES_PER_FRAME)
    data = reorder(input_data)

    if len(data) == LED_COUNT * 3:
        for i in range(LED_COUNT):
            r = data[i * 3]
            g = data[i * 3 + 1]
            b = data[i * 3 + 2]
            np[i] = (r, g, b)
        np.write()

        # Optional: echo same data back
        # sys.stdout.buffer.write(bytes(data))
        # sys.stdout.flush()
