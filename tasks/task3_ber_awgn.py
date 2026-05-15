"""実施内容3: AWGN環境でのQPSK BER測定。"""

from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import numpy as np

from src.ber import calc_ber, db_to_linear, qpsk_theoretical_ber
from src.channel import add_awgn_for_gamma_b
from src.plot_utils import ensure_output_dirs, setup_matplotlib
from src.qpsk_demodulator import demodulate_qpsk
from src.qpsk_modulator import modulate_qpsk


GAMMA_B_DB = np.array([-6, -3, 0, 3, 6, 9], dtype=float)
BIT_COUNT = 200_000
SEED = 43


def run_ber_measurement() -> list[dict[str, float]]:
    rng = np.random.default_rng(SEED)
    bits = rng.integers(0, 2, size=BIT_COUNT, dtype=int)
    mod_result = modulate_qpsk(bits)

    rows: list[dict[str, float]] = []
    for index, gamma_db in enumerate(GAMMA_B_DB):
        rx_signal = add_awgn_for_gamma_b(mod_result.passband, gamma_db, seed=SEED + index + 1)
        demod_result = demodulate_qpsk(rx_signal)
        measured = calc_ber(bits, demod_result.bits)
        theoretical = qpsk_theoretical_ber(db_to_linear(gamma_db))
        rows.append(
            {
                "gamma_b_db": float(gamma_db),
                "theoretical_ber": float(theoretical),
                "measured_ber": float(measured),
                "bit_errors": float(np.sum(bits != demod_result.bits)),
            }
        )
    return rows


def save_table(rows: list[dict[str, float]]) -> None:
    csv_path = Path("outputs/tables/task3_ber_awgn.csv")
    md_path = Path("outputs/tables/task3_ber_awgn.md")
    header = "gamma_b_db,theoretical_ber,measured_ber,bit_errors"
    csv_lines = [header]
    md_lines = [
        "| gamma_b [dB] | 理論値 | 測定値 | 誤りビット数 |",
        "| ---: | ---: | ---: | ---: |",
    ]
    for row in rows:
        csv_lines.append(
            f"{row['gamma_b_db']:.0f},{row['theoretical_ber']:.8e},"
            f"{row['measured_ber']:.8e},{int(row['bit_errors'])}"
        )
        md_lines.append(
            f"| {row['gamma_b_db']:.0f} | {row['theoretical_ber']:.3e} | "
            f"{row['measured_ber']:.3e} | {int(row['bit_errors'])} |"
        )
    csv_path.write_text("\n".join(csv_lines) + "\n", encoding="utf-8")
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def plot_ber(rows: list[dict[str, float]], output_path: Path) -> None:
    setup_matplotlib()
    import matplotlib.pyplot as plt

    gamma = np.array([row["gamma_b_db"] for row in rows])
    theory = np.array([row["theoretical_ber"] for row in rows])
    measured = np.array([row["measured_ber"] for row in rows])

    fig, ax = plt.subplots(figsize=(7, 5), constrained_layout=True)
    ax.semilogy(gamma, theory, "-o", label="Theoretical BER")
    ax.semilogy(gamma, measured, "s--", label="Measured BER")
    ax.set_xlabel("SNR per bit $\\gamma_b$ [dB]")
    ax.set_ylabel("$P_b$")
    ax.set_title("Task 3 QPSK BER in AWGN")
    ax.set_ylim(1e-6, 1)
    ax.grid(True, which="both")
    ax.legend()
    fig.savefig(output_path, dpi=300)
    plt.close(fig)


def write_report(rows: list[dict[str, float]]) -> None:
    table = "\n".join(
        f"| {row['gamma_b_db']:.0f} | {row['theoretical_ber']:.3e} | "
        f"{row['measured_ber']:.3e} | {int(row['bit_errors'])} |"
        for row in rows
    )
    Path("reports/task3_ber_awgn.md").write_text(
        "# 実施内容3 QPSKのBER特性\n\n"
        "## 目的\n\n"
        "QPSK帯域信号に白色ガウス雑音を加え、ビット当たり信号対雑音電力比 `gamma_b` を変化させたときのBERを測定し、理論値と比較する。\n\n"
        "## 条件\n\n"
        f"- 情報ビット数 `{BIT_COUNT}`\n"
        f"- 乱数seed `{SEED}`\n"
        "- 伝搬路応答 `h = 1`\n"
        "- 測定点 `gamma_b = -6, -3, 0, 3, 6, 9 dB`\n\n"
        "## 結果\n\n"
        "| gamma_b [dB] | 理論値 | 測定値 | 誤りビット数 |\n"
        "| ---: | ---: | ---: | ---: |\n"
        f"{table}\n\n"
        "BER曲線は `outputs/figures/task3_ber_awgn.png` に保存した。\n\n"
        "## 考察下書き\n\n"
        "測定BERは `gamma_b` が大きくなるにつれて低下し、QPSKの理論BER `P_b = Q(sqrt(2 gamma_b))` と同じ傾向を示した。高SNRでは誤り数が少なくなるため、有限ビット数のシミュレーションでは測定値のばらつきが相対的に大きくなる。\n",
        encoding="utf-8",
    )


def main() -> None:
    ensure_output_dirs()
    rows = run_ber_measurement()
    save_table(rows)
    plot_ber(rows, Path("outputs/figures/task3_ber_awgn.png"))
    write_report(rows)

    print("実施内容3 完了")
    for row in rows:
        print(
            f"gamma_b={row['gamma_b_db']:.0f} dB: "
            f"theory={row['theoretical_ber']:.3e}, "
            f"measured={row['measured_ber']:.3e}, "
            f"errors={int(row['bit_errors'])}"
        )
    print("図: outputs/figures/task3_ber_awgn.png")
    print("表: outputs/tables/task3_ber_awgn.csv")


if __name__ == "__main__":
    main()
