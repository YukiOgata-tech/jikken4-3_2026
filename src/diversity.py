"""Diversity combining utilities."""

from __future__ import annotations

import numpy as np


def combine_two_timeslots(rx_slot1: np.ndarray, rx_slot2: np.ndarray) -> np.ndarray:
    """Combine two received time slots from the same antenna by summation."""
    slot1 = np.asarray(rx_slot1, dtype=complex)
    slot2 = np.asarray(rx_slot2, dtype=complex)
    if slot1.shape != slot2.shape:
        raise ValueError("Time slot arrays must have the same shape.")
    return slot1 + slot2


def channel_power_weights(*channels: complex) -> np.ndarray:
    """Return normalized weights proportional to channel power."""
    powers = np.array([abs(channel) ** 2 for channel in channels], dtype=float)
    if np.all(powers == 0):
        raise ValueError("At least one channel must be non-zero.")
    return powers / np.sum(powers)


def combine_equalized_antennas(equalized_antennas: list[np.ndarray], weights: np.ndarray) -> np.ndarray:
    """Weighted-combine equalized antenna symbols."""
    if len(equalized_antennas) != len(weights):
        raise ValueError("Number of antenna arrays and weights must match.")
    combined = np.zeros_like(np.asarray(equalized_antennas[0], dtype=complex))
    for symbols, weight in zip(equalized_antennas, weights):
        combined = combined + weight * np.asarray(symbols, dtype=complex)
    return combined
