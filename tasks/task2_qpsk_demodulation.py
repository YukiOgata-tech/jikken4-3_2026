"""実施内容2: QPSK復調回路の作成と復元結果の出力。"""

from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from src.config import SAMPLES_PER_SYMBOL, T
from src.plot_utils import ensure_output_dirs, setup_matplotlib
from src.qpsk_demodulator import demodulate_qpsk
from src.qpsk_modulator import modulate_qpsk


def plot_task2(mod_result, demod_result, output_path: Path) -> None:
    setup_matplotlib()
    import matplotlib.pyplot as plt

    time_over_t = demod_result.time / T
    symbol_index = np.arange(demod_result.symbol_i.size)
    pair_labels = ["".join(str(int(bit)) for bit in pair) for pair in mod_result.bit_pairs]

    fig = plt.figure(figsize=(12, 10), constrained_layout=True)
    fig.suptitle("Task 2 QPSK Demodulation Waveforms", fontsize=14)
    axes = [
        fig.add_subplot(5, 2, 1),
        fig.add_subplot(5, 2, 3),
        fig.add_subplot(5, 2, 5),
        fig.add_subplot(5, 2, 7),
        fig.add_subplot(5, 2, 9),
        fig.add_subplot(5, 2, 2),
        fig.add_subplot(5, 2, 4),
        fig.add_subplot(5, 2, 6),
        fig.add_subplot(5, 2, 8),
        fig.add_subplot(5, 2, 10),
    ]

    left_series = [
        (mod_result.symbol_i, symbol_index, "$u_I$", "index", "stem"),
        (mod_result.symbol_q, symbol_index, "$u_Q$", "index", "stem"),
        (mod_result.baseband_i, mod_result.time / T, "$u_I(t)$", "$t/T$", "line"),
        (mod_result.baseband_q, mod_result.time / T, "$u_Q(t)$", "$t/T$", "line"),
        (mod_result.passband, mod_result.time / T, "$s(t)$", "$t/T$", "line"),
    ]
    right_series = [
        (demod_result.passband, time_over_t, "$r(t)$", "$t/T$", "line"),
        (demod_result.mixed_i, time_over_t, "$r_I(t)$", "$t/T$", "line"),
        (demod_result.mixed_q, time_over_t, "$r_Q(t)$", "$t/T$", "line"),
        (demod_result.symbol_i, symbol_index, "$\\hat{u}_I$", "index", "stem"),
        (demod_result.symbol_q, symbol_index, "$\\hat{u}_Q$", "index", "stem"),
    ]

    for axis, (values, x_values, ylabel, xlabel, style) in zip(axes[:5], left_series):
        if style == "stem":
            axis.stem(x_values, values)
            for x, label in zip(symbol_index, pair_labels):
                axis.text(x, 1.25, f"'{label}'", ha="center", fontsize=8)
        else:
            axis.plot(x_values, values, "-o", markersize=3)
        axis.set_ylabel(ylabel)
        axis.set_xlabel(xlabel)
        axis.set_xlim(0, mod_result.symbol_i.size)
        axis.set_ylim(-2.0, 2.0)
        axis.grid(True)

    for axis, (values, x_values, ylabel, xlabel, style) in zip(axes[5:], right_series):
        if style == "stem":
            axis.stem(x_values, values)
        else:
            axis.plot(x_values, values, "-o", markersize=3)
        axis.set_ylabel(ylabel)
        axis.set_xlabel(xlabel)
        axis.set_xlim(0, mod_result.symbol_i.size)
        axis.set_ylim(-2.0, 2.0)
        axis.grid(True)

    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def plot_constellation(demod_result, output_path: Path) -> None:
    setup_matplotlib()
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(6, 6), constrained_layout=True)
    ax.scatter(
        demod_result.symbol_i,
        demod_result.symbol_q,
        alpha=0.6,
        s=100,
        label="Demodulated symbols",
        zorder=2,
    )
    ax.scatter(
        [np.sqrt(0.5), -np.sqrt(0.5), -np.sqrt(0.5), np.sqrt(0.5)],
        [np.sqrt(0.5), np.sqrt(0.5), -np.sqrt(0.5), -np.sqrt(0.5)],
        marker="x",
        color="red",
        s=120,
        label="Ideal symbols",
        zorder=3,
    )
    ax.axhline(0, color="black", linewidth=0.8)
    ax.axvline(0, color="black", linewidth=0.8)
    ax.set_xlabel("Inphase")
    ax.set_ylabel("Quadrature")
    ax.set_title("Task 2 Demodulated Constellation")
    ax.set_xlim(-1.5, 1.5)
    ax.set_ylim(-1.5, 1.5)
    ax.grid(True)
    ax.legend()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def main() -> None:
    ensure_output_dirs()
    bits = np.array([int(ch) for ch in "101101110001"], dtype=int)
    mod_result = modulate_qpsk(bits)
    demod_result = demodulate_qpsk(mod_result.passband)
    bit_errors = int(np.sum(bits != demod_result.bits))

    waveform_path = Path("outputs/figures/task2_qpsk_demodulation_waveforms.png")
    constellation_path = Path("outputs/figures/task2_qpsk_demodulation_constellation.png")
    plot_task2(mod_result, demod_result, waveform_path)
    plot_constellation(demod_result, constellation_path)

    log_path = Path("outputs/logs/task2_qpsk_demodulation.txt")
    lines = [
        "Task 2 QPSK demodulation",
        f"tx_bits: {''.join(str(int(bit)) for bit in bits)}",
        f"rx_bits: {''.join(str(int(bit)) for bit in demod_result.bits)}",
        f"bit_errors: {bit_errors}",
        f"samples_per_symbol: {SAMPLES_PER_SYMBOL}",
        "index,u_hat_I,u_hat_Q",
    ]
    for index, (ui, uq) in enumerate(zip(demod_result.symbol_i, demod_result.symbol_q)):
        lines.append(f"{index},{ui:.12f},{uq:.12f}")
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("実施内容2 完了")
    print(f"送信ビット列: {''.join(str(int(bit)) for bit in bits)}")
    print(f"復元ビット列: {''.join(str(int(bit)) for bit in demod_result.bits)}")
    print(f"ビット誤り数: {bit_errors}")
    print(f"図: {waveform_path}")
    print(f"図: {constellation_path}")
    print(f"ログ: {log_path}")


if __name__ == "__main__":
    main()
