"""実施内容4: data1.xlsxの伝搬路推定、等化、データ復元。"""

from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from src.ber import calc_ber, count_bit_errors
from src.equalizer import equalize_symbols, estimate_channel_from_preamble
from src.io_utils import describe_xlsx, read_bit_column, read_complex_signal, split_frame
from src.plot_utils import ensure_output_dirs, setup_matplotlib
from src.qpsk_demodulator import symbols_to_bits
from src.qpsk_modulator import qpsk_map_bits_to_symbols


DATA_PATH = Path("docs/data1.xlsx")
PREAMBLE_SYMBOLS = 16


def plot_constellations(rx_data, eq_data, output_path: Path) -> None:
    setup_matplotlib()
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)
    for ax, symbols, title in [
        (axes[0], rx_data, "Before Equalization"),
        (axes[1], eq_data, "After Equalization"),
    ]:
        ax.scatter(symbols.real, symbols.imag)
        ax.axhline(0, color="black", linewidth=0.8)
        ax.axvline(0, color="black", linewidth=0.8)
        ax.set_title(title)
        ax.set_xlabel("Inphase")
        ax.set_ylabel("Quadrature")
        ax.set_xlim(-2, 2)
        ax.set_ylim(-2, 2)
        ax.grid(True)
    fig.suptitle("Task 4 data1 Constellation")
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def main() -> None:
    ensure_output_dirs()
    structure_log = describe_xlsx(DATA_PATH)
    Path("outputs/logs/task4_data1_xlsx_structure.txt").write_text(structure_log + "\n", encoding="utf-8")

    preamble_bits = read_bit_column(DATA_PATH, "プリアンブルビット系列")
    data_bits = read_bit_column(DATA_PATH, "データ系列")
    rx_symbols = read_complex_signal(DATA_PATH, "変調信号")
    rx_pre, rx_data = split_frame(rx_symbols, PREAMBLE_SYMBOLS)

    tx_pre, _ = qpsk_map_bits_to_symbols(preamble_bits)
    h_hat = estimate_channel_from_preamble(rx_pre, tx_pre)
    eq_data = equalize_symbols(rx_data, h_hat)
    recovered_bits = symbols_to_bits(eq_data)
    bit_errors = count_bit_errors(data_bits, recovered_bits)
    ber = calc_ber(data_bits, recovered_bits)

    plot_constellations(rx_data, eq_data, Path("outputs/figures/task4_data1_constellation.png"))

    log_lines = [
        "Task 4 data1 equalization",
        f"h_hat_real: {h_hat.real:.12f}",
        f"h_hat_imag: {h_hat.imag:.12f}",
        f"h_hat_abs: {abs(h_hat):.12f}",
        f"h_hat_angle_deg: {np.degrees(np.angle(h_hat)):.12f}",
        f"tx_data_bits: {''.join(str(int(bit)) for bit in data_bits)}",
        f"rx_data_bits: {''.join(str(int(bit)) for bit in recovered_bits)}",
        f"bit_errors: {bit_errors}",
        f"ber: {ber:.12e}",
    ]
    Path("outputs/logs/task4_data1_equalization.txt").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    Path("outputs/tables/task4_data1_recovered_bits.txt").write_text(
        "".join(str(int(bit)) for bit in recovered_bits) + "\n", encoding="utf-8"
    )
    Path("reports/task4_data1_equalization.md").write_text(
        "# 実施内容4 data1.xlsxの復調\n\n"
        "## 目的\n\n"
        "`data1.xlsx` に保存された受信基底帯域信号から、既知プリアンブルを用いて伝搬路応答を推定し、データビット列を復元する。\n\n"
        "## 方法\n\n"
        "受信フレームをプリアンブル16シンボルとデータ32シンボルに分割した。プリアンブルビット列をQPSKシンボルへ写像し、受信プリアンブルとの相互相関から伝搬路応答 `h` を推定した。データシンボルを `h` で除算して等化し、象限判定によりビット列を復元した。\n\n"
        "## 結果\n\n"
        f"- 推定伝搬路応答 `h = {h_hat.real:.6f} + j{h_hat.imag:.6f}`\n"
        f"- `|h| = {abs(h_hat):.6f}`\n"
        f"- `angle(h) = {np.degrees(np.angle(h_hat)):.3f} deg`\n"
        f"- ビット誤り数 `{bit_errors}`\n"
        f"- BER `{ber:.3e}`\n\n"
        "等化前後のシンボル点配置は `outputs/figures/task4_data1_constellation.png` に保存した。\n\n"
        "## 考察下書き\n\n"
        "等化前の受信シンボルは伝搬路応答により振幅減衰と位相回転を受けている。プリアンブルは送信側で既知であるため、受信プリアンブルとの対応から伝搬路応答を推定できる。推定値でデータシンボルを除算すると、シンボル点が理想的なQPSK配置へ近づき、データビット列を復元できる。\n",
        encoding="utf-8",
    )

    print("実施内容4 完了")
    print(f"h_hat = {h_hat.real:.6f} + j{h_hat.imag:.6f}")
    print(f"|h_hat| = {abs(h_hat):.6f}, angle = {np.degrees(np.angle(h_hat)):.3f} deg")
    print(f"復元ビット列: {''.join(str(int(bit)) for bit in recovered_bits)}")
    print(f"ビット誤り数: {bit_errors}, BER: {ber:.3e}")
    print("図: outputs/figures/task4_data1_constellation.png")
    print("ログ: outputs/logs/task4_data1_equalization.txt")


if __name__ == "__main__":
    main()
