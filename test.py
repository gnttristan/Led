import numpy as np

size = 200
amplitudes = np.random.rand(60)

groups_indexes = np.cumsum(np.repeat(size / amplitudes.shape[0], amplitudes.shape[0], )).astype(int)
diff_indexes = np.hstack((groups_indexes[0], np.diff(groups_indexes)))
return np.repeat(amplitudes, diff_indexes)