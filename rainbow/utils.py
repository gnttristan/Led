import numpy as np

from config import FREQ_BINS


def apply_amplitudes_rgb(rainbow_rgb, amplitudes_from_eq):
    return np.clip(rainbow_rgb + (amplitudes_from_eq.reshape(-1, 1) * 128), 0, 255)

def apply_energy_alpha(energy_detected):
    min_alpha = 0
    alpha = (1 - (1 - min_alpha) * energy_detected) * 255
    alpha_array = np.repeat(alpha, FREQ_BINS)

    return alpha_array

def concatenate_rgb_alpha(rainbow_rgb, alpha):
    return np.concatenate([rainbow_rgb, alpha[:, np.newaxis]], axis=1)