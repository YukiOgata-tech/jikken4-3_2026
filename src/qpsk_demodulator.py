"""QPSK demodulation utilities."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from src.config import FC, SAMPLES_PER_SYMBOL, TS


@dataclass(frozen=True)
class QPSKDemodulationResult:
    passband: np.ndarray
    time: np.ndarray
    mixed_i: np.ndarray
    mixed_q: np.ndarray
    symbol_i: np.ndarray
    symbol_q: np.ndarray
    symbols: np.ndarray
    bits: np.ndarray


def coherent_demodulate(passband_signal: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Multiply the passband signal by coherent I/Q carriers."""
    passband = np.asarray(passband_signal, dtype=float).reshape(-1)
    time = np.arange(passband.size) * TS
    mixed_i = passband * 2 * np.cos(2 * math.pi * FC * time)
    mixed_q = passband * -2 * np.sin(2 * math.pi * FC * time)
    return mixed_i, mixed_q, time


def integrate_symbols(
    i_wave: np.ndarray,
    q_wave: np.ndarray,
    samples_per_symbol: int = SAMPLES_PER_SYMBOL,
) -> tuple[np.ndarray, np.ndarray]:
    """Average I/Q demodulated waveforms over each symbol interval."""
    i_array = np.asarray(i_wave, dtype=float).reshape(-1)
    q_array = np.asarray(q_wave, dtype=float).reshape(-1)
    if i_array.size != q_array.size:
        raise ValueError("I and Q waveforms must have the same length.")
    if i_array.size % samples_per_symbol != 0:
        raise ValueError("Waveform length must be a multiple of samples_per_symbol.")

    i_symbols = i_array.reshape(-1, samples_per_symbol).mean(axis=1)
    q_symbols = q_array.reshape(-1, samples_per_symbol).mean(axis=1)
    return i_symbols, q_symbols


def decision_from_iq(i_values: np.ndarray, q_values: np.ndarray) -> np.ndarray:
    """Make QPSK hard decisions from I/Q symbol samples."""
    i_array = np.asarray(i_values, dtype=float).reshape(-1)
    q_array = np.asarray(q_values, dtype=float).reshape(-1)
    if i_array.size != q_array.size:
        raise ValueError("I and Q symbol arrays must have the same length.")

    bits: list[int] = []
    for i_value, q_value in zip(i_array, q_array):
        if i_value >= 0 and q_value >= 0:
            bits.extend([0, 0])
        elif i_value < 0 and q_value >= 0:
            bits.extend([0, 1])
        elif i_value < 0 and q_value < 0:
            bits.extend([1, 1])
        else:
            bits.extend([1, 0])
    return np.array(bits, dtype=int)


def decision_qpsk(symbols: np.ndarray) -> np.ndarray:
    """Make QPSK hard decisions from complex symbols."""
    symbols_array = np.asarray(symbols, dtype=complex).reshape(-1)
    return decision_from_iq(symbols_array.real, symbols_array.imag)


def symbols_to_bits(symbols: np.ndarray) -> np.ndarray:
    """Alias for QPSK hard decision on complex symbols."""
    return decision_qpsk(symbols)


def demodulate_qpsk(passband_signal: np.ndarray) -> QPSKDemodulationResult:
    """Run the complete coherent QPSK demodulation chain."""
    passband = np.asarray(passband_signal, dtype=float).reshape(-1)
    mixed_i, mixed_q, time = coherent_demodulate(passband)
    symbol_i, symbol_q = integrate_symbols(mixed_i, mixed_q)
    symbols = symbol_i + 1j * symbol_q
    bits = decision_from_iq(symbol_i, symbol_q)
    return QPSKDemodulationResult(
        passband=passband,
        time=time,
        mixed_i=mixed_i,
        mixed_q=mixed_q,
        symbol_i=symbol_i,
        symbol_q=symbol_q,
        symbols=symbols,
        bits=bits,
    )
