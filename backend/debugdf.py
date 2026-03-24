import time

import pandas
import numpy as np

i = 0
dataframe = np.zeros(90)
while i < 300:
    visual_update()
    # msg = protocol_byting(gradient_rainbow.data[:300])
    msg_bytes = (rgbp_pipeline.output_rgb[:30] * 2).astype(np.int32).astype(np.uint8).flatten()
    dataframe = np.vstack((dataframe, msg_bytes))
    # hdr = b'\xAA' + bytes([seq]) + struct.pack('>H', len(msg_bytes))
    # c = crc16(hdr + msg_bytes)
    # frame = hdr + msg_bytes + struct.pack('>H', c)

    # try:
    #     ser.write(msg_bytes)
    #     # print(len(msg_bytes))
    #     print(msg_bytes)
    #     # ser.flush()
    # except serial.SerialTimeoutException:
    #     pass
    #     print("Serial buffer full, skipping frame")

    # reply = ser.read(len(msg_bytes))
    # print(bytes(reply[:3]))
    # seq = (seq + 1) & 0xFF
    i += 1
    time.sleep(0.05)

pddf = pandas.DataFrame(dataframe.tolist())
pddf.to_csv("./dataframes/pddf.csv")