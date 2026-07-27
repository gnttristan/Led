import socket
import time
import numpy as np

ESP32_IP = "192.168.1.17"
ESP32_DDP_PORT = 4048
LED_COUNT = 300
FPS = 20

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send_ddp(rgb: np.ndarray):
    rgb = np.asarray(rgb, dtype=np.uint8)

    if rgb.shape != (LED_COUNT, 3):
        raise ValueError(f"Expected shape {(LED_COUNT, 3)}, got {rgb.shape}")

    packet = bytes([0x41, 0, 0x01, 1]) + (0).to_bytes(4, "big") + len(rgb.tobytes()).to_bytes(2, "big") + rgb.tobytes()

    sent = sock.sendto(packet, (ESP32_IP, ESP32_DDP_PORT))

    print(
        f"sent={sent} bytes "
        f"payload={len(rgb.tobytes())} "
        f"first_led={rgb[0].tolist()} "
        f"target={ESP32_IP}:{ESP32_DDP_PORT}"
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

    send_ddp(rgb)
    time.sleep(1 / FPS)
