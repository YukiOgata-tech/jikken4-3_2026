"""Channel and noise utilities."""

from __future__ import annotations

import numpy as np

from src.config import FS, R
from src.ber import db_to_linear


def add_awgn(signal: np.ndarray, snr_db: float, seed: int | None = None) -> np.ndarray:
    """Add real AWGN to a passband signal for a given SNR."""
    signal_array = np.asarray(signal, dtype=float)
    snr_linear = db_to_linear(snr_db)
    signal_power = np.mean(signal_array**2)
    noise_power = signal_power / snr_linear
    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, np.sqrt(noise_power), size=signal_array.shape)
    return signal_array + noise


def add_awgn_for_gamma_b(
    signal: np.ndarray,
    gamma_b_db: float,
    alpha: float = 1.0,
    seed: int | None = None,
) -> np.ndarray:
    """Add real passband AWGN according to the experiment text gamma_b relation."""
    gamma_b = db_to_linear(gamma_b_db)
    sigma_z_squared = alpha**2 * FS / (8 * R * gamma_b)
    rng = np.random.default_rng(seed)
    noise = rng.normal(0.0, np.sqrt(sigma_z_squared), size=np.asarray(signal).shape)
    return np.asarray(signal, dtype=float) + noise


def generate_complex_awgn(size: int | tuple[int, ...], noise_power: float, seed: int | None = None) -> np.ndarray:
    """Generate circularly symmetric complex AWGN with total power noise_power."""
    rng = np.random.default_rng(seed)
    std = np.sqrt(noise_power / 2)
    return rng.normal(0.0, std, size=size) + 1j * rng.normal(0.0, std, size=size)


def apply_channel(symbols: np.ndarray, h: complex, noise_power: float = 0.0, seed: int | None = None) -> np.ndarray:
    """Apply a flat complex channel and optional complex AWGN."""
    symbols_array = np.asarray(symbols, dtype=complex)
    noise = 0.0
    if noise_power > 0:
        noise = generate_complex_awgn(symbols_array.shape, noise_power, seed=seed)
    return h * symbols_array + noise
