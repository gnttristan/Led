import machine
import neopixel
import time
import sys
import ubinascii

LED_COUNT = 300
LED_PIN = 0
np = neopixel.NeoPixel(machine.Pin(LED_PIN), LED_COUNT)

START = 0xAA
HEADER_LEN = 1 + 1 + 2   # start + seq + len
CRC_LEN = 2

# simple CRC16-CCITT implementation
def crc16_ccitt(data, poly=0x1021, init=0xFFFF):
    crc = init
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) & 0xFFFF) ^ poly
            else:
                crc = (crc << 1) & 0xFFFF
    return crc & 0xFFFF

def read_from_stdin(n):
    # small wrapper like before
    buf = bytearray(n)
    mv = memoryview(buf)
    got = 0
    while got < n:
        chunk = sys.stdin.buffer.read(n - got)
        if not chunk:
            time.sleep(0.001)
            continue
        mv[got:got+len(chunk)] = chunk
        got += len(chunk)
    return buf

buf = bytearray()

while True:
    # read whatever is available in small chunks to keep CPU low
    chunk = sys.stdin.buffer.read(256)
    if not chunk:
        time.sleep(0.002)
        continue
    buf.extend(chunk)

    # look for start marker and process full frames
    while True:
        idx = buf.find(bytes([START]))
        if idx == -1:
            # no start marker yet; keep last 1 byte in case marker spans reads
            if len(buf) > 1_000:
                del buf[:-1]
            break

        # remove leading junk before start
        if idx > 0:
            del buf[:idx]

        if len(buf) < HEADER_LEN:
            # need more bytes for header
            break

        # parse header
        seq = buf[1]
        length = (buf[2] << 8) | buf[3]
        total_len = HEADER_LEN + length + CRC_LEN
        if len(buf) < total_len:
            # incomplete frame — wait for more bytes
            break

        frame = bytes(buf[:total_len])
        payload = frame[HEADER_LEN:HEADER_LEN+length]
        recv_crc = (frame[-2] << 8) | frame[-1]
        calc_crc = crc16_ccitt(frame[:-2])

        if calc_crc == recv_crc:
            # good frame — apply payload (expecting 900 bytes -> 300 * 3)
            if length == LED_COUNT * 3:
                for i in range(LED_COUNT):
                    r = payload[i*3]
                    g = payload[i*3 + 1]
                    b = payload[i*3 + 2]
                    np[i] = (r, g, b)
                np.write()
            # else: ignore or handle different lengths
            del buf[:total_len]
        else:
            # bad CRC — drop the start byte and resync
            del buf[0]
