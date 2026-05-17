import argparse
import glob
import os
import subprocess
import sys


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


def find_firmware():
    candidates = []

    for root, _, files in os.walk(os.getcwd()):
        for filename in files:
            if filename.lower().endswith(".bin") and "esp32" in filename.lower():
                candidates.append(os.path.join(root, filename))

    candidates = sorted(candidates)

    if not candidates:
        raise RuntimeError(
            "No ESP32 firmware .bin found. Download one from "
            "https://micropython.org/download/ESP32_GENERIC/ and pass it with "
            "`--firmware path/to/ESP32_GENERIC-xxx.bin`."
        )

    if len(candidates) > 1:
        firmware_list = "\n".join(f"  - {path}" for path in candidates)
        raise RuntimeError(
            "More than one ESP32 firmware .bin found:\n"
            f"{firmware_list}\n"
            "Run again with `--firmware path/to/firmware.bin`."
        )

    return candidates[0]


def run(command):
    print("+", " ".join(command))
    subprocess.run(command, check=True)


def main():
    parser = argparse.ArgumentParser(description="Erase and flash MicroPython to ESP32.")
    parser.add_argument(
        "--firmware",
        help="Path to ESP32 MicroPython firmware .bin. Auto-detected if omitted.",
    )
    parser.add_argument(
        "--port",
        help="ESP32 serial port. Auto-detected from /dev/cu.* if omitted.",
    )
    parser.add_argument("--baud", default="460800", help="Flash baud rate.")
    args = parser.parse_args()

    port = args.port or find_esp32_port()
    firmware = args.firmware or find_firmware()

    print(f"Using port: {port}")
    print(f"Using firmware: {firmware}")

    run([sys.executable, "-m", "esptool", "--chip", "esp32", "--port", port, "erase_flash"])
    run(
        [
            sys.executable,
            "-m",
            "esptool",
            "--chip",
            "esp32",
            "--port",
            port,
            "--baud",
            args.baud,
            "write_flash",
            "-z",
            "0x1000",
            firmware,
        ]
    )


if __name__ == "__main__":
    main()
