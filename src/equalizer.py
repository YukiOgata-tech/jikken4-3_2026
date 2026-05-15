"""Channel estimation and equalization utilities."""

from __future__ import annotations

import numpy as np


def estimate_channel_from_preamble(rx_pre_symbols: np.ndarray, tx_pre_symbols: np.ndarray) -> complex:
    """Estimate a flat channel from received and transmitted preamble symbols."""
    rx = np.asarray(rx_pre_symbols, dtype=complex).reshape(-1)
    tx = np.asarray(tx_pre_symbols, dtype=complex).reshape(-1)
    if rx.size != tx.size:
        raise ValueError("rx_pre_symbols and tx_pre_symbols must have the same length.")
    denominator = np.vdot(tx, tx)
    if denominator == 0:
        raise ValueError("Preamble symbol power is zero.")
    return np.vdot(tx, rx) / denominator


def equalize_symbols(rx_symbols: np.ndarray, h_hat: complex) -> np.ndarray:
    """Equalize symbols by dividing by the estimated flat channel."""
    if abs(h_hat) == 0:
        raise ValueError("Estimated channel must be non-zero.")
    return np.asarray(rx_symbols, dtype=complex) / h_hat
