"""実施内容1: QPSK変調回路の作成と送信側波形の出力。"""

from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from src.config import R, SAMPLES_PER_SYMBOL, T
from src.plot_utils import ensure_output_dirs, setup_matplotlib
from src.qpsk_modulator import modulate_qpsk


def plot_task1(result, output_path: Path) -> None:
    setup_matplotlib()
    import matplotlib.pyplot as plt

    symbol_index = np.arange(result.symbol_i.size)
    time_over_t = result.time / T
    pair_labels = ["".join(str(int(bit)) for bit in pair) for pair in result.bit_pairs]

    fig, axes = plt.subplots(5, 1, figsize=(8, 9), constrained_layout=True)
    fig.suptitle("Task 1 QPSK Modulation Waveforms", fontsize=14)

    axes[0].stem(symbol_index, result.symbol_i)
    axes[0].set_ylabel("$u_I$")
    axes[0].set_xlabel("index")
    axes[0].set_xlim(0, result.symbol_i.size)
    axes[0].set_ylim(-1.5, 1.5)
    axes[0].grid(True)

    axes[1].stem(symbol_index, result.symbol_q)
    axes[1].set_ylabel("$u_Q$")
    axes[1].set_xlabel("index")
    axes[1].set_xlim(0, result.symbol_q.size)
    axes[1].set_ylim(-1.5, 1.5)
    axes[1].grid(True)

    axes[2].step(time_over_t, result.baseband_i, where="post")
    axes[2].plot(time_over_t, result.baseband_i, "o", markersize=3)
    axes[2].set_ylabel("$u_I(t)$")
    axes[2].set_xlabel("$t/T$")
    axes[2].set_xlim(0, result.symbol_i.size)
    axes[2].set_ylim(-1.5, 1.5)
    axes[2].grid(True)

    axes[3].step(time_over_t, result.baseband_q, where="post")
    axes[3].plot(time_over_t, result.baseband_q, "o", markersize=3)
    axes[3].set_ylabel("$u_Q(t)$")
    axes[3].set_xlabel("$t/T$")
    axes[3].set_xlim(0, result.symbol_i.size)
    axes[3].set_ylim(-1.5, 1.5)
    axes[3].grid(True)

    axes[4].plot(time_over_t, result.passband, "-o", markersize=3)
    axes[4].set_ylabel("$s(t)$")
    axes[4].set_xlabel("$t/T$")
    axes[4].set_xlim(0, result.symbol_i.size)
    axes[4].set_ylim(-1.5, 1.5)
    axes[4].grid(True)

    for axis in axes[:2]:
        for x, label in zip(symbol_index, pair_labels):
            axis.text(x, 1.25, f"'{label}'", ha="center", fontsize=9)

    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def main() -> None:
    ensure_output_dirs()
    bits = np.array([int(ch) for ch in "101101110001"], dtype=int)
    result = modulate_qpsk(bits)

    output_path = Path("outputs/figures/task1_qpsk_modulation.png")
    plot_task1(result, output_path)

    log_path = Path("outputs/logs/task1_qpsk_modulation.txt")
    lines = [
        "Task 1 QPSK modulation",
        f"bits: {''.join(str(int(bit)) for bit in result.bits)}",
        f"symbols: {result.symbols.size}",
        f"samples_per_symbol: {SAMPLES_PER_SYMBOL}",
        f"symbol_rate_R: {R}",
        f"symbol_period_T: {T}",
        "bit_pairs,u_I,u_Q,phase_rad",
    ]
    for pair, ui, uq, phase in zip(result.bit_pairs, result.symbol_i, result.symbol_q, result.phases):
        label = "".join(str(int(bit)) for bit in pair)
        lines.append(f"{label},{ui:.12f},{uq:.12f},{phase:.12f}")
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("実施内容1 完了")
    print(f"入力ビット列: {''.join(str(int(bit)) for bit in result.bits)}")
    print(f"シンボル数: {result.symbols.size}")
    print(f"図: {output_path}")
    print(f"ログ: {log_path}")


if __name__ == "__main__":
    main()
