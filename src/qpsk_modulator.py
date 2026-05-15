"""QPSK modulation utilities."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from src.config import FC, SAMPLES_PER_SYMBOL, TS


BITS_TO_PHASE = {
    (0, 0): math.pi / 4,
    (0, 1): 3 * math.pi / 4,
    (1, 1): 5 * math.pi / 4,
    (1, 0): 7 * math.pi / 4,
}


@dataclass(frozen=True)
class QPSKModulationResult:
    bits: np.ndarray
    bit_pairs: np.ndarray
    phases: np.ndarray
    symbols: np.ndarray
    symbol_i: np.ndarray
    symbol_q: np.ndarray
    baseband_i: np.ndarray
    baseband_q: np.ndarray
    baseband: np.ndarray
    passband: np.ndarray
    time: np.ndarray


def bits_to_pairs(bits: np.ndarray | list[int]) -> np.ndarray:
    """Convert a flat bit array into two-bit QPSK symbols."""
    bits_array = np.asarray(bits, dtype=int).reshape(-1)
    if bits_array.size % 2 != 0:
        raise ValueError("QPSK modulation requires an even number of bits.")
    if not np.isin(bits_array, [0, 1]).all():
        raise ValueError("Bits must contain only 0 or 1.")
    return bits_array.reshape(-1, 2)


def qpsk_map_bits_to_symbols(bits: np.ndarray | list[int]) -> tuple[np.ndarray, np.ndarray]:
    """Map bit pairs to unit-energy QPSK complex symbols."""
    pairs = bits_to_pairs(bits)
    phases = np.array([BITS_TO_PHASE[tuple(pair)] for pair in pairs], dtype=float)
    symbols = np.exp(1j * phases)
    return symbols, phases


def symbols_to_iq(symbols: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Return in-phase and quadrature components from complex symbols."""
    symbols_array = np.asarray(symbols, dtype=complex)
    return symbols_array.real, symbols_array.imag


def rect_pulse_shape(values: np.ndarray, samples_per_symbol: int = SAMPLES_PER_SYMBOL) -> np.ndarray:
    """Apply rectangular pulse shaping by repeating each symbol value."""
    if samples_per_symbol <= 0:
        raise ValueError("samples_per_symbol must be positive.")
    return np.repeat(np.asarray(values), samples_per_symbol)


def generate_baseband(bits: np.ndarray | list[int]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate rectangular-pulse-shaped complex baseband signal."""
    symbols, _ = qpsk_map_bits_to_symbols(bits)
    symbol_i, symbol_q = symbols_to_iq(symbols)
    baseband_i = rect_pulse_shape(symbol_i)
    baseband_q = rect_pulse_shape(symbol_q)
    return baseband_i + 1j * baseband_q, baseband_i, baseband_q


def generate_passband(bits: np.ndarray | list[int]) -> tuple[np.ndarray, np.ndarray]:
    """Generate QPSK passband signal from bits."""
    baseband, _, _ = generate_baseband(bits)
    time = np.arange(baseband.size) * TS
    carrier = np.exp(1j * 2 * math.pi * FC * time)
    passband = np.real(baseband * carrier)
    return passband, time


def modulate_qpsk(bits: np.ndarray | list[int]) -> QPSKModulationResult:
    """Run the complete QPSK modulation chain."""
    bits_array = np.asarray(bits, dtype=int).reshape(-1)
    pairs = bits_to_pairs(bits_array)
    symbols, phases = qpsk_map_bits_to_symbols(bits_array)
    symbol_i, symbol_q = symbols_to_iq(symbols)
    baseband_i = rect_pulse_shape(symbol_i)
    baseband_q = rect_pulse_shape(symbol_q)
    baseband = baseband_i + 1j * baseband_q
    time = np.arange(baseband.size) * TS
    carrier = np.exp(1j * 2 * math.pi * FC * time)
    passband = np.real(baseband * carrier)
    return QPSKModulationResult(
        bits=bits_array,
        bit_pairs=pairs,
        phases=phases,
        symbols=symbols,
        symbol_i=symbol_i,
        symbol_q=symbol_q,
        baseband_i=baseband_i,
        baseband_q=baseband_q,
        baseband=baseband,
        passband=passband,
        time=time,
    )
