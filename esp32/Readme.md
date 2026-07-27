  python3 -m venv .venv-pio
  source .venv-pio/bin/activate
  python -m pip install -U pip platformio

  pio run -d esp32
  pio run -d esp32 -t upload \
    --upload-port /dev/cu.usbserial-14240