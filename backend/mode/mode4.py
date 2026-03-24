import time

import serial
import numpy as np
from backend.pipelines.visual.rgbp_pipeline import RGBPPipeline
from backend.pipelines.transforms.value_transformer import ValueTransformerPipeline
from backend.pipelines.visual.whitening_pipeline import WhiteningPipeline
from backend.updatable.updatable import visual_updatable_objects, audio_updatable_objects
from backend.amplitudes.amplitudes import Amplitudes
from backend.buffer.buffer import Buffer
from backend.config import *
from backend.energy.energy_bass import EnergyBassDetector
from backend.rainbow.gradient_rainbow import GradiantRainbow
from backend.stream.stream import Stream
from crcmod.predefined import mkPredefinedCrcFun  # pip install crcmod


crc16 = mkPredefinedCrcFun('crc-ccitt-false')
seq = 0

chunk_data = np.zeros(CHUNK_SIZE)
def audio_update(indata, frames, time, status):
    global chunk_data
    chunk_data[:] = indata.flatten()

    for obj in audio_updatable_objects:
        obj.update()

def visual_update():
    for obj in visual_updatable_objects:
        obj.update()

main_stream = Stream(callback=audio_update)

buffer = Buffer(indata=chunk_data)

amplitudes = Amplitudes(
    buffer=buffer,
    powering=0.8,
    normalisation=True,
    log=1.5
)

energy_bass_detector = EnergyBassDetector(
    buffer=buffer,
)

# tempo_detector = TempoDetector(
#     spikes=energy_bass_detector.data,
# )

gradient_rainbow = GradiantRainbow(inv_fraction=3)

# energy_to_alpha_pipeline = EnergyToAlphaPipeline(
#     energy=energy_bass_detector.kick_energy_ratio
# )

whitening_pipeline = WhiteningPipeline(
    input_rgb=gradient_rainbow.data,
    white_level=energy_bass_detector.kick_energy_ratio
)

value_transformer_pipeline = ValueTransformerPipeline(
    input_value=amplitudes.data,
    input_value_interval=[0, 1],
    output_value_interval=[50, 255],
    power=4
)

rgbp_pipeline = RGBPPipeline(
    rgb = whitening_pipeline.output_rgb,
    alpha = value_transformer_pipeline.output_value
)

# spectrogram_chart = SpectrogramChart(
#     data=np.ones(amplitudes.data.shape),
#     title="Amplitudes",
#     number_points=amplitudes.data.shape[0],
#     left_label="Frequency",
#     bottom_label="Amplitude",
#     brushes=rgbp_pipeline.output_rgb,
# )

# line_chart = LineChart(
#     input_data=energy_bass_detector.kick_energy_ratio,
#     title="Energy Kick Ratio",
#     number_points=100,
#     left_label="Energy",
#     bottom_label="Time"
# )

# win = spectrogram_chart.draw()
# win2 = line_chart.draw()

main_stream.start()

ser = serial.Serial(
    port='COM20',
    baudrate=115200,
    timeout=0,
    write_timeout=0.1
)

def protocol_byting(array):
    packet_size = 64
    nb_position_bytes = np.ceil(np.size(array) / (packet_size - 1))
    gd_allonged = np.hstack((array.flatten(), np.zeros((packet_size - 1) - np.mod(np.size(array), (packet_size - 1)))))
    gd_packeted = gd_allonged.reshape((int(nb_position_bytes), packet_size - 1))
    gd_byted = np.hstack((np.arange(nb_position_bytes)[:, None], gd_packeted))
    return gd_byted.flatten()

while True:
    visual_update()
    # msg = protocol_byting(gradient_rainbow.data[:300])
    msg_bytes = np.clip((rgbp_pipeline.output_rgb[:300] - 10) / 3, 5, 90).astype(np.int32)
    # hdr = b'\xAA' + bytes([seq]) + struct.pack('>H', len(msg_bytes))
    # c = crc16(hdr + msg_bytes)
    # frame = hdr + msg_bytes + struct.pack('>H', c)

    if np.sum(msg_bytes) != 0:
        try:
            ser.write(msg_bytes.clip(0, 255).astype(np.uint8).tobytes())
            # print(len(msg_bytes))
            print(msg_bytes)
            # ser.flush()
        except serial.SerialTimeoutException:
            pass
            print("Serial buffer full, skipping frame")

        # reply = ser.read(len(msg_bytes))
        # print(bytes(reply[:3]))
        # seq = (seq + 1) & 0xFF
        time.sleep(0.05)