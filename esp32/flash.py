import argparse
import glob
import subprocess
from pathlib import Path


PORT_PATTERNS = (
    "/dev/cu.wchusbserial*",
    "/dev/cu.usbserial*",
    "/dev/cu.SLAB_USBtoUART*",
    "/dev/cu.usbmodem*",
)


def find_esp32_port():
    ports = []

    for pattern in PORT_PATTERNS:
        ports.extend(glob.glob(pattern))

    ports = sorted(set(ports))

    if not ports:
        raise RuntimeError(
            "No ESP32 serial port found. Plug the board in and check `ls /dev/cu.*`."
        )

    if len(ports) > 1:
        port_list = "\n".join(f"  - {port}" for port in ports)
        raise RuntimeError(
            "More than one possible ESP32 serial port found:\n"
            f"{port_list}\n"
            "Run again with `--port /dev/cu...`."
        )

    return ports[0]


def run(command):
    print("+", " ".join(command))
    subprocess.run(command, check=True)


def main():
    parser = argparse.ArgumentParser(description="Build and flash the native ESP32 firmware.")
    parser.add_argument(
        "--port",
        help="ESP32 serial port. Auto-detected from /dev/cu.* if omitted.",
    )
    parser.add_argument("--baud", default="460800", help="Upload baud rate.")
    args = parser.parse_args()

    port = args.port or find_esp32_port()
    project_dir = Path(__file__).resolve().parent

    print(f"Using port: {port}")
    run(["pio", "run", "-d", str(project_dir), "-t", "upload", "--upload-port", port,
         "--upload-speed", args.baud])


if __name__ == "__main__":
    main()
