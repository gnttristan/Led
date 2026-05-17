import numpy as np

a = np.random.rand(300)
b = np.random.rand(100)

ratio = a.shape[-1] / b.shape[-1]
broadcast_indexes = np.floor(np.cumsum(np.repeat(ratio, b.shape[-1])) - ratio).astype(np.int16)

