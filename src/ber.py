"""Bit error rate utilities."""

from __future__ import annotations

import math

import numpy as np


def count_bit_errors(tx_bits: np.ndarray, rx_bits: np.ndarray) -> int:
    tx = np.asarray(tx_bits, dtype=int).reshape(-1)
    rx = np.asarray(rx_bits, dtype=int).reshape(-1)
    if tx.size != rx.size:
        raise ValueError("tx_bits and rx_bits must have the same length.")
    return int(np.sum(tx != rx))


def calc_ber(tx_bits: np.ndarray, rx_bits: np.ndarray) -> float:
    tx = np.asarray(tx_bits, dtype=int).reshape(-1)
    if tx.size == 0:
        raise ValueError("Bit arrays must not be empty.")
    return count_bit_errors(tx, rx_bits) / tx.size


def q_function(x: float | np.ndarray) -> float | np.ndarray:
    values = np.asarray(x, dtype=float)
    erfc_values = np.vectorize(lambda value: 0.5 * math.erfc(value / math.sqrt(2)))(values)
    if np.isscalar(x):
        return float(erfc_values)
    return erfc_values


def qpsk_theoretical_ber(gamma_b_linear: float | np.ndarray) -> float | np.ndarray:
    gamma = np.asarray(gamma_b_linear, dtype=float)
    values = np.vectorize(lambda value: 0.5 * math.erfc(math.sqrt(value)))(gamma)
    if np.isscalar(gamma_b_linear):
        return float(values)
    return values


def db_to_linear(x_db: float | np.ndarray) -> float | np.ndarray:
    return 10 ** (np.asarray(x_db, dtype=float) / 10)


def linear_to_db(x: float | np.ndarray) -> float | np.ndarray:
    return 10 * np.log10(np.asarray(x, dtype=float))
