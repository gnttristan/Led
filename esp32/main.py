import machine
import neopixel
import sys
import time

# Change this to the ESP32 GPIO connected to your LED strip data input.
# Use the GPIO number, not a board label like "D5".
LED_PIN = 5
LED_COUNT = 100

BYTES_PER_FRAME = LED_COUNT * 3
STARTUP_COLOR = (0, 1, 0)
BOOT_DELAY_SECONDS = 1
DEBUG = False
DEBUG_FULL_FRAME = False
DEBUG_PREVIEW_LEDS = 10
DEBUG_LOG_FILE = "debug.log"


def log(message):
    if DEBUG:
        line = str(message) + "\n"
        print(line, end="")
        try:
            with open(DEBUG_LOG_FILE, "a") as log_file:
                log_file.write(line)
        except OSError:
            pass


def log_frame(frame):
    if not DEBUG:
        return

    if DEBUG_FULL_FRAME:
        log("frame=" + repr(list(frame)))
        return

    preview_size = min(DEBUG_PREVIEW_LEDS * 3, len(frame))
    log(
        "frame len={} preview={} checksum={}".format(
            len(frame),
            list(frame[:preview_size]),
            sum(frame) % 256,
        )
    )


def clear_log_file():
    if DEBUG:
        try:
            with open(DEBUG_LOG_FILE, "w") as log_file:
                log_file.write("")
        except OSError:
            pass


def write_startup_pattern(strip):
    for i in range(LED_COUNT):
        strip[i] = STARTUP_COLOR
    strip.write()


def apply_frame(strip, frame):
    for i in range(LED_COUNT):
        offset = i * 3
        strip[i] = (frame[offset], frame[offset + 1], frame[offset + 2])
    strip.write()


def main():
    clear_log_file()
    log("esp32/main.py starting")
    log("led_pin={} led_count={} bytes_per_frame={}".format(LED_PIN, LED_COUNT, BYTES_PER_FRAME))

    strip = neopixel.NeoPixel(machine.Pin(LED_PIN, machine.Pin.OUT), LED_COUNT)
    write_startup_pattern(strip)
    log("startup pattern written; waiting {}s".format(BOOT_DELAY_SECONDS))
    time.sleep(BOOT_DELAY_SECONDS)
    log("ready for rgb frames")

    while True:
        log("TRUE")
        frame = sys.stdin.buffer.read(BYTES_PER_FRAME)
        log(f"frame : {frame}")
        log(f"len(frame) : {BYTES_PER_FRAME}")
        if frame and len(frame) == BYTES_PER_FRAME:
            log_frame(frame)
            apply_frame(strip, frame)

main()
