"""実施内容5: data2.xlsxのダイバーシチ合成とデータ復元。"""

from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from src.ber import calc_ber, count_bit_errors
from src.diversity import channel_power_weights, combine_equalized_antennas, combine_two_timeslots
from src.equalizer import equalize_symbols, estimate_channel_from_preamble
from src.io_utils import describe_xlsx, read_bit_column, read_complex_signal, split_frame
from src.plot_utils import ensure_output_dirs, setup_matplotlib
from src.qpsk_demodulator import symbols_to_bits
from src.qpsk_modulator import qpsk_map_bits_to_symbols


DATA_PATH = Path("docs/data2.xlsx")
PREAMBLE_SYMBOLS = 16
SIGNAL_SHEETS = [
    "変調信号(Ant１，TS１）",
    "変調信号(Ant１，TS２）",
    "変調信号(Ant２，TS１）",
    "変調信号(Ant２，TS２）",
]


def read_frames() -> dict[str, tuple[np.ndarray, np.ndarray]]:
    frames = {}
    for sheet in SIGNAL_SHEETS:
        symbols = read_complex_signal(DATA_PATH, sheet)
        frames[sheet] = split_frame(symbols, PREAMBLE_SYMBOLS)
    return frames


def estimate_antenna_channel(rx_pre_1: np.ndarray, rx_pre_2: np.ndarray, tx_pre: np.ndarray) -> complex:
    rx_concat = np.concatenate([rx_pre_1, rx_pre_2])
    tx_concat = np.concatenate([tx_pre, tx_pre])
    return estimate_channel_from_preamble(rx_concat, tx_concat)


def plot_task5(single_symbols, combined_symbols, output_path: Path) -> None:
    setup_matplotlib()
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 5), constrained_layout=True)
    for ax, symbols, title in [
        (axes[0], single_symbols, "Best Single Frame"),
        (axes[1], combined_symbols, "Diversity Combined"),
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
    fig.suptitle("Task 5 data2 Diversity Combining")
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def main() -> None:
    ensure_output_dirs()
    Path("outputs/logs/task5_data2_xlsx_structure.txt").write_text(
        describe_xlsx(DATA_PATH) + "\n", encoding="utf-8"
    )

    preamble_bits = read_bit_column(DATA_PATH, "プリアンブルビット系列")
    data_bits = read_bit_column(DATA_PATH, "データ系列")
    tx_pre, _ = qpsk_map_bits_to_symbols(preamble_bits)
    frames = read_frames()

    ant1_ts1_pre, ant1_ts1_data = frames[SIGNAL_SHEETS[0]]
    ant1_ts2_pre, ant1_ts2_data = frames[SIGNAL_SHEETS[1]]
    ant2_ts1_pre, ant2_ts1_data = frames[SIGNAL_SHEETS[2]]
    ant2_ts2_pre, ant2_ts2_data = frames[SIGNAL_SHEETS[3]]

    h1 = estimate_antenna_channel(ant1_ts1_pre, ant1_ts2_pre, tx_pre)
    h2 = estimate_antenna_channel(ant2_ts1_pre, ant2_ts2_pre, tx_pre)
    weights = channel_power_weights(h1, h2)

    single_results = []
    for sheet, (rx_pre, rx_data), h in [
        (SIGNAL_SHEETS[0], frames[SIGNAL_SHEETS[0]], h1),
        (SIGNAL_SHEETS[1], frames[SIGNAL_SHEETS[1]], h1),
        (SIGNAL_SHEETS[2], frames[SIGNAL_SHEETS[2]], h2),
        (SIGNAL_SHEETS[3], frames[SIGNAL_SHEETS[3]], h2),
    ]:
        eq_data = equalize_symbols(rx_data, h)
        bits = symbols_to_bits(eq_data)
        single_results.append(
            {
                "name": sheet,
                "symbols": eq_data,
                "bits": bits,
                "errors": count_bit_errors(data_bits, bits),
                "ber": calc_ber(data_bits, bits),
            }
        )
    best_single = min(single_results, key=lambda item: item["errors"])

    ant1_sum_pre = combine_two_timeslots(ant1_ts1_pre, ant1_ts2_pre)
    ant2_sum_pre = combine_two_timeslots(ant2_ts1_pre, ant2_ts2_pre)
    ant1_sum_data = combine_two_timeslots(ant1_ts1_data, ant1_ts2_data)
    ant2_sum_data = combine_two_timeslots(ant2_ts1_data, ant2_ts2_data)

    # The summed signal contains two copies of the same transmitted symbol.
    ant1_eq = equalize_symbols(ant1_sum_data, h1) / 2
    ant2_eq = equalize_symbols(ant2_sum_data, h2) / 2
    ant1_bits = symbols_to_bits(ant1_eq)
    ant2_bits = symbols_to_bits(ant2_eq)

    combined_symbols = combine_equalized_antennas([ant1_eq, ant2_eq], weights)
    combined_bits = symbols_to_bits(combined_symbols)
    combined_errors = count_bit_errors(data_bits, combined_bits)
    combined_ber = calc_ber(data_bits, combined_bits)

    plot_task5(best_single["symbols"], combined_symbols, Path("outputs/figures/task5_data2_diversity.png"))

    lines = [
        "Task 5 data2 diversity combining",
        f"h1_real: {h1.real:.12f}",
        f"h1_imag: {h1.imag:.12f}",
        f"h1_abs: {abs(h1):.12f}",
        f"h1_angle_deg: {np.degrees(np.angle(h1)):.12f}",
        f"h2_real: {h2.real:.12f}",
        f"h2_imag: {h2.imag:.12f}",
        f"h2_abs: {abs(h2):.12f}",
        f"h2_angle_deg: {np.degrees(np.angle(h2)):.12f}",
        f"weight_ant1: {weights[0]:.12f}",
        f"weight_ant2: {weights[1]:.12f}",
        "",
        "single_frame_results",
    ]
    for result in single_results:
        lines.append(f"{result['name']}: errors={result['errors']}, ber={result['ber']:.12e}")
    lines.extend(
        [
            "",
            f"ant1_two_slot_errors: {count_bit_errors(data_bits, ant1_bits)}",
            f"ant2_two_slot_errors: {count_bit_errors(data_bits, ant2_bits)}",
            f"combined_errors: {combined_errors}",
            f"combined_ber: {combined_ber:.12e}",
            f"tx_data_bits: {''.join(str(int(bit)) for bit in data_bits)}",
            f"combined_bits: {''.join(str(int(bit)) for bit in combined_bits)}",
        ]
    )
    Path("outputs/logs/task5_data2_diversity.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    Path("outputs/tables/task5_data2_recovered_bits.txt").write_text(
        "".join(str(int(bit)) for bit in combined_bits) + "\n", encoding="utf-8"
    )

    single_table = "\n".join(
        f"| {result['name']} | {result['errors']} | {result['ber']:.3e} |"
        for result in single_results
    )
    Path("reports/task5_data2_diversity.md").write_text(
        "# 実施内容5 data2.xlsxのダイバーシチ合成\n\n"
        "## 目的\n\n"
        "`data2.xlsx` に含まれる2アンテナ、2タイムスロットの受信基底帯域信号を合成し、データビット列を復元する。\n\n"
        "## 方法\n\n"
        "各アンテナでは2つのタイムスロットが同じ伝搬路応答を持つとみなし、2つの受信プリアンブルをまとめて伝搬路応答を推定した。各アンテナの2タイムスロットを加算し、推定伝搬路応答で等化した。アンテナ間の重みはチャネル電力 `|h|^2` に比例させ、等化後シンボルを重み付き合成した。\n\n"
        "## 結果\n\n"
        f"- `h1 = {h1.real:.6f} + j{h1.imag:.6f}`, `|h1| = {abs(h1):.6f}`\n"
        f"- `h2 = {h2.real:.6f} + j{h2.imag:.6f}`, `|h2| = {abs(h2):.6f}`\n"
        f"- 重み `w1 = {weights[0]:.6f}`, `w2 = {weights[1]:.6f}`\n"
        f"- アンテナ1の2スロット合成誤り数 `{count_bit_errors(data_bits, ant1_bits)}`\n"
        f"- アンテナ2の2スロット合成誤り数 `{count_bit_errors(data_bits, ant2_bits)}`\n"
        f"- 2アンテナ合成誤り数 `{combined_errors}`\n"
        f"- 2アンテナ合成BER `{combined_ber:.3e}`\n\n"
        "### 単一フレーム結果\n\n"
        "| フレーム | 誤り数 | BER |\n"
        "| --- | ---: | ---: |\n"
        f"{single_table}\n\n"
        "合成前後のシンボル点配置は `outputs/figures/task5_data2_diversity.png` に保存した。\n\n"
        "## 考察下書き\n\n"
        "同一アンテナの2タイムスロットを加算すると、信号成分は同相に加算される一方、雑音は独立に加算されるためSNRが改善する。さらに、アンテナ間では受信電力が異なるため、チャネル電力の大きいアンテナを重くする重み付き合成が有効である。今回の配布データではアンテナ1の受信品質が高く、アンテナ1の2スロット合成だけで0誤りとなった。一方で、低SNRのアンテナ2を理論重みで少量加えた2アンテナ合成では1ビット誤りが残った。これは64ビットという短いデータ系列では、平均SNRを最大化する重みが必ずしも観測された有限系列の誤り数を最小にしないためである。単一の低SNRフレームでは誤りが多く、品質の高いアンテナを重く扱う必要があることを確認できる。\n",
        encoding="utf-8",
    )

    print("実施内容5 完了")
    print(f"h1 = {h1.real:.6f} + j{h1.imag:.6f}, |h1|={abs(h1):.6f}")
    print(f"h2 = {h2.real:.6f} + j{h2.imag:.6f}, |h2|={abs(h2):.6f}")
    print(f"weights = [{weights[0]:.6f}, {weights[1]:.6f}]")
    for result in single_results:
        print(f"{result['name']}: errors={result['errors']}, BER={result['ber']:.3e}")
    print(f"ant1 two-slot errors={count_bit_errors(data_bits, ant1_bits)}")
    print(f"ant2 two-slot errors={count_bit_errors(data_bits, ant2_bits)}")
    print(f"combined errors={combined_errors}, BER={combined_ber:.3e}")
    print(f"復元ビット列: {''.join(str(int(bit)) for bit in combined_bits)}")
    print("図: outputs/figures/task5_data2_diversity.png")
    print("ログ: outputs/logs/task5_data2_diversity.txt")


if __name__ == "__main__":
    main()
