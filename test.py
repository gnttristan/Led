import socket
import time
import numpy as np

WLED_IP = "192.168.1.17"
WLED_UDP_PORT = 21324
LED_COUNT = 300
FPS = 20

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_drgb(rgb: np.ndarray):
    rgb = np.asarray(rgb, dtype=np.uint8)

    if rgb.shape != (LED_COUNT, 3):
        raise ValueError(f"Expected shape {(LED_COUNT, 3)}, got {rgb.shape}")

    # WLED UDP Realtime:
    # byte 0 = 2 -> DRGB
    # byte 1 = timeout in seconds
    # bytes 2+ = R,G,B,R,G,B...
    packet = bytes([2, 2]) + rgb.tobytes()

    sent = sock.sendto(packet, (WLED_IP, WLED_UDP_PORT))

    print(
        f"sent={sent} bytes "
        f"payload={len(rgb.tobytes())} "
        f"first_led={rgb[0].tolist()} "
        f"target={WLED_IP}:{WLED_UDP_PORT}"
    )

while True:
    # Change this to test colors
    rgb = np.zeros((LED_COUNT, 3), dtype=np.uint8)

    # Test 1: all black
    # rgb[:, :] = [0, 0, 0]

    # Test 2: all red
    rgb[:, :] = [255, 0, 0]

    # Test 3: all green
    # rgb[:, :] = [0, 255, 0]

    # Test 4: all blue
    # rgb[:, :] = [0, 0, 255]

    send_drgb(rgb)
    time.sleep(1 / FPS)