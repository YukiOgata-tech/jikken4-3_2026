# Codex 指示書：実験Ⅳ-3 デジタル変復調回路

このリポジトリは、電子情報通信実験Ⅳ-3「デジタル変復調回路」の実施内容1〜5をPythonで実装し、レポート用の図表・結果・考察下書きを作成するための作業用リポジトリである。

Codexは、この指示書を読んだうえで、リポジトリ全体の構成を維持しながら、Pythonコード、出力結果、レポート下書きを作成すること。

---

## 1。最重要方針

- `docs/EIC_Lab4/` はGitHubからcloneした参考コード置き場である。
- `docs/EIC_Lab4/` 内のファイルは編集しない。
- 必要な処理は参考コードを読み取り、`src/` 配下に再実装する。
- Notebook依存にはしない。
- 実施内容1〜5は、それぞれ `tasks/` 配下のPythonファイルから実行できるようにする。
- 図、表、ログ、復元ビット列などはすべて `outputs/` 配下に保存する。
- レポートに記載する説明、結果、考察の下書きを `reports/` 配下にMarkdownで作成する。
- ソースコードは最終的にZip提出するため、処理を整理する。
- すべてのtaskはリポジトリルートから実行できるようにする。
- 日本語の文章では句読点を「、。」に統一する。
- 図にはタイトル、軸ラベル、凡例を付ける。
- 保存する図はレポートに貼れる品質にする。可能なら `dpi=300` で保存する。
- 乱数を使う処理では再現性のためseedを設定する。
- data1.xlsx、data2.xlsxの列構造が想定と違う場合は、勝手に決め打ちせず、まず読み取り結果を `outputs/logs/` に保存し、その構造に合わせて処理する。
- 実行結果の要約を各taskの最後に標準出力する。
- エラーが出た場合は、原因が分かるように例外メッセージを出す。

---

## 2。既存ディレクトリ構成

現在のリポジトリ構成は以下である。

```text
jikken4-3/
├ README.md
├ requirements.txt
├ .gitignore
│
├ docs/
│   ├ Lab4-3.pdf
│   ├ Lab4-3slides.pdf
│   ├ data1.xlsx
│   ├ data2.xlsx
│   └ EIC_Lab4/
│
├ src/
│
├ tasks/
│
├ outputs/
│   ├ figures/
│   ├ tables/
│   └ logs/
│
├ reports/
│
└ submission/
```

---

## 3。まず確認する資料

以下を確認してから実装すること。

1. `docs/Lab4-3.pdf`
2. `docs/Lab4-3slides.pdf`
3. `docs/data1.xlsx`
4. `docs/data2.xlsx`
5. `docs/EIC_Lab4/` 内の参考コード

特に、スライド側では `data1.xlsx`、`data2.xlsx` は基底帯域信号系列として説明されている。  
旧テキストでは `data1.csv`、`data2.csv` と書かれている箇所があるが、このリポジトリでは実際に配布された `data1.xlsx`、`data2.xlsx` を使用する。

最初にExcelのシート名、列名、先頭行、値の型を確認し、ログに保存すること。

---

## 4。実験パラメータ

資料の表1に基づき、以下を共通パラメータとして使う。

```text
搬送波周波数 fc = 100 Hz
シンボルレート R = 100 symbols/s
シンボル周期 T = 0.01 s
サンプリング周波数 Fs = 1000 Hz
サンプル周期 Ts = 0.001 s
```

これらは `src/config.py` に定義する。

---

## 5。作成するPythonファイル

### 5.1 src/

共通処理を `src/` に入れる。

```text
src/
├ __init__.py
├ config.py
├ qpsk_modulator.py
├ qpsk_demodulator.py
├ channel.py
├ ber.py
├ equalizer.py
├ diversity.py
├ io_utils.py
└ plot_utils.py
```

各ファイルの役割は以下とする。

### `src/config.py`

共通パラメータを定義する。

- `FC = 100`
- `R = 100`
- `T = 1 / R`
- `FS = 1000`
- `TS = 1 / FS`
- `SAMPLES_PER_SYMBOL = int(FS / R)`

### `src/qpsk_modulator.py`

QPSK変調に関する関数を置く。

想定関数：

- `bits_to_pairs(bits)`
- `qpsk_map_bits_to_symbols(bits)`
- `symbols_to_iq(symbols)`
- `rect_pulse_shape(values, samples_per_symbol)`
- `generate_baseband(bits)`
- `generate_passband(bits)`
- `modulate_qpsk(bits)`

QPSKマッピングは以下とする。

```text
00 → π/4
01 → 3π/4
11 → 5π/4
10 → 7π/4
```

複素シンボルは以下で表す。

```text
u_i = exp(jθ_i)
```

### `src/qpsk_demodulator.py`

QPSK復調に関する関数を置く。

想定関数：

- `coherent_demodulate(passband_signal)`
- `integrate_symbols(i_wave, q_wave)`
- `decision_qpsk(symbols)`
- `symbols_to_bits(symbols)`
- `demodulate_qpsk(passband_signal)`
- `decision_from_iq(i_values, q_values)`

象限判定は以下とする。

```text
I > 0, Q > 0 → 00
I < 0, Q > 0 → 01
I < 0, Q < 0 → 11
I > 0, Q < 0 → 10
```

### `src/channel.py`

通信路、雑音、伝搬路応答を扱う。

想定関数：

- `add_awgn(signal, snr_db)`
- `add_awgn_for_gamma_b(signal, gamma_b_db)`
- `apply_channel(symbols, h, noise_power)`
- `generate_complex_awgn(size, noise_power, seed=None)`

### `src/ber.py`

BER測定と理論値計算を扱う。

想定関数：

- `count_bit_errors(tx_bits, rx_bits)`
- `calc_ber(tx_bits, rx_bits)`
- `q_function(x)`
- `qpsk_theoretical_ber(gamma_b_linear)`
- `db_to_linear(x_db)`
- `linear_to_db(x)`

理論BER：

```text
P_b(γ_b) = Q(sqrt(2γ_b))
```

### `src/equalizer.py`

伝搬路推定と等化を扱う。

想定関数：

- `estimate_channel_from_preamble(rx_pre_symbols, tx_pre_symbols)`
- `equalize_symbols(rx_symbols, h_hat)`

伝搬路応答推定は以下とする。

```text
h_hat = (1 / N_pre) Σ u_hat_pre,i × conj(u_pre,i)
```

等化は以下とする。

```text
u_equalized_i = u_hat_i / h_hat
```

### `src/diversity.py`

実施内容5の複数信号合成を扱う。

想定関数：

- `combine_simple_average(equalized_symbol_sets)`
- `combine_weighted(equalized_symbol_sets, weights)`
- `estimate_weights_from_channel(h_values)`
- `combine_data2_frames(...)`

基本方針：

- 各受信系列をまずプリアンブルで等化する。
- 単純平均を実装する。
- `|h|^2` に比例する重み付き合成も実装する。
- スライドHintに基づく最適重みについて、可能な範囲で検討し、レポートに説明する。

### `src/io_utils.py`

Excel読込、CSV保存、ログ保存を扱う。

想定関数：

- `inspect_excel(path)`
- `read_excel_sheets(path)`
- `save_dataframe(df, path)`
- `save_text(text, path)`
- `ensure_dir(path)`

### `src/plot_utils.py`

図の描画と保存を扱う。

想定関数：

- `plot_task1_waveforms(...)`
- `plot_task2_waveforms(...)`
- `plot_ber_curve(...)`
- `plot_constellation(...)`
- `save_figure(path)`

---

## 6。tasks/

実施内容1〜5の入口を入れる。

```text
tasks/
├ task1_modulation.py
├ task2_demodulation.py
├ task3_ber.py
├ task4_data1_equalization.py
└ task5_data2_diversity.py
```

各taskは、リポジトリルートから以下のように実行できるようにする。

```bash
python tasks/task1_modulation.py
python tasks/task2_demodulation.py
python tasks/task3_ber.py
python tasks/task4_data1_equalization.py
python tasks/task5_data2_diversity.py
```

---

## 7。実施内容1：QPSK変調回路

### 7.1 目的

情報ビット列 `101101110001` をQPSK変調し、図6(a)に対応する送信側波形を作成する。

### 7.2 実装内容

- 情報ビット列を2ビットごとに分割する。
- QPSKのグレイ符号マッピングを行う。

```text
00 → π/4
01 → 3π/4
11 → 5π/4
10 → 7π/4
```

- シンボル点を複素数で表す。

```text
u_i = exp(jθ_i)
u_I = cos(θ_i)
u_Q = sin(θ_i)
```

- 矩形パルス整形により、基底帯域信号 `u_I(t)`、`u_Q(t)` を作成する。
- 搬送波を用いて帯域信号 `s(t)` を作成する。

```text
s(t) = u_I(t) cos(2πf_c t) - u_Q(t) sin(2πf_c t)
```

### 7.3 出力

以下を保存する。

```text
outputs/figures/task1/qpsk_modulation_waveform.png
outputs/logs/task1_result.txt
```

必要なら、以下も保存する。

```text
outputs/tables/task1_symbols.csv
```

### 7.4 レポート下書き

`reports/task1_report.md` を作成し、以下を含める。

- 実施内容の説明
- 使用したビット列
- QPSKマッピング
- 出力図の貼付先
- 図6(a)と対応していることの説明
- 簡単な考察

### 7.5 考察の方向性

- QPSKでは2ビットごとに1つのシンボルとして扱われる。
- シンボル周期ごとに搬送波の位相が変化する。
- 基底帯域信号のI成分、Q成分により帯域信号が生成される。
- 図6(a)と同様に、送信側でビット列に応じた位相変化が確認できる。

---

## 8。実施内容2：QPSK復調回路

### 8.1 目的

実施内容1で生成したQPSK変調信号を復調し、元の情報ビット列 `101101110001` を復元する。

### 8.2 実装内容

- 受信信号に以下を乗算する。

```text
r_I(t) = r(t) × 2cos(2πf_c t)
r_Q(t) = r(t) × -2sin(2πf_c t)
```

- シンボル周期ごとに積分または平均化し、推定シンボル点を得る。

```text
u_hat_I,i
u_hat_Q,i
u_hat_i = u_hat_I,i + j u_hat_Q,i
```

- 象限判定でビット列に戻す。

```text
I > 0, Q > 0 → 00
I < 0, Q > 0 → 01
I < 0, Q < 0 → 11
I > 0, Q < 0 → 10
```

- 復元ビット列が元のビット列と一致するか確認する。

### 8.3 出力

```text
outputs/figures/task2/qpsk_demodulation_waveform.png
outputs/tables/task2_decoded_bits.csv
outputs/logs/task2_result.txt
```

### 8.4 レポート下書き

`reports/task2_report.md` を作成し、以下を含める。

- 復調手順
- 同期検波と積分の説明
- 復元ビット列
- 元ビット列との一致確認
- 図6(b)と対応していることの説明
- 簡単な考察

### 8.5 考察の方向性

- 搬送波の同相成分、直交成分を乗算することでI成分、Q成分が得られる。
- 積分により搬送波周波数の2倍成分が除去され、基底帯域成分が取り出される。
- 雑音や伝搬路歪みがない場合、元のビット列が誤りなく復元される。

---

## 9。実施内容3：熱雑音を加えたBER評価

### 9.1 目的

QPSK信号に白色ガウス雑音を加え、ビット誤り率BERを測定し、理論値と比較する。

### 9.2 実装内容

- 20,000 bits以上のランダムビット列を生成する。
- QPSK変調する。
- 伝搬路応答は `h = 1`、つまり `α = 1`、`φ = 0` とする。
- SNRまたは `γ_b` を変化させて白色ガウス雑音を加える。
- 復調後のビット列と送信ビット列を比較し、BERを求める。

BER：

```text
BER = 誤りビット数 / 全ビット数
```

理論値：

```text
P_b(γ_b) = Q(sqrt(2γ_b))
```

表2に対応する `γ_b[dB]` は以下を使う。

```text
-6, -3, 0, 3, 6, 9
```

### 9.3 出力

```text
outputs/tables/task3_ber_table.csv
outputs/figures/task3/ber_curve.png
outputs/logs/task3_result.txt
```

`task3_ber_table.csv` には以下の列を含める。

```text
gamma_b_db
theoretical_ber
measured_ber
bit_errors
num_bits
```

### 9.4 レポート下書き

`reports/task3_report.md` を作成し、以下を含める。

- 雑音付加の説明
- SNRとγ_bの関係
- BER測定方法
- 表2相当の表
- BER特性図
- 理論値と測定値の比較
- 高SNRほどBERが低下することの考察
- 測定値が理論値と完全一致しない理由

### 9.5 考察の方向性

- 雑音電力が大きい、すなわちSNRが小さい場合、コンステレーション点が大きくばらつくため、象限判定の誤りが増える。
- γ_bが大きくなると、シンボル点が理想点付近に集中し、BERが低下する。
- 測定値は有限ビット数で評価しているため、理論値と完全には一致しない。
- 高SNR領域では誤り数が少なくなるため、測定BERのばらつきが大きくなりやすい。

---

## 10。実施内容4：data1.xlsxの復調と伝搬路等化

### 10.1 目的

`data1.xlsx` に保存されたQPSK信号を復調し、データビット列を復元する。

### 10.2 注意

スライドでは `data1.xlsx` は基底帯域信号系列として説明されている。  
したがって、最初にExcelの列構造を確認し、I成分、Q成分、プリアンブル、データ、元データ列がどこにあるかを調べること。

### 10.3 実装内容

- `data1.xlsx` を読み込む。
- 列名、シート名、データ構造を確認し、その概要をログに保存する。
- フレーム構造は以下とする。

```text
プリアンブル：16シンボル、32ビット
データ：32シンボル、64ビット
```

- 既知の送信プリアンブル `u_pre,i` と受信プリアンブル `u_hat_pre,i` から伝搬路応答を推定する。

```text
h_hat = (1 / N_pre) Σ u_hat_pre,i × conj(u_pre,i)
```

- 受信シンボル点を補償する。

```text
u_equalized_i = u_hat_i / h_hat
```

- 等化前後のコンステレーションを保存する。
- 等化後のシンボル点からデータビット列を復元する。
- data1.xlsx内に元のデータ系列がある場合は比較し、誤り数を出す。

### 10.4 出力

```text
outputs/figures/task4/constellation_before_equalization.png
outputs/figures/task4/constellation_after_equalization.png
outputs/tables/task4_decoded_bits.csv
outputs/logs/task4_result.txt
```

必要なら以下も出力する。

```text
outputs/tables/task4_excel_structure.csv
outputs/tables/task4_channel_estimate.csv
```

### 10.5 レポート下書き

`reports/task4_report.md` を作成し、以下を含める。

- data1.xlsxの構造
- プリアンブルとデータ部の説明
- 伝搬路応答推定の説明
- 等化前後のコンステレーション図
- 復元ビット列
- 元データとの比較
- 等化によりシンボル点配置が補正されたことの考察

### 10.6 考察の方向性

- 伝搬路応答により、受信シンボルは振幅変化と位相回転を受ける。
- 等化前はコンステレーションが理想位置から回転、縮小、拡大している可能性がある。
- プリアンブルを用いて伝搬路応答を推定し、受信シンボルを補償することで、理想的なQPSKシンボル点に近づく。
- これにより象限判定が可能となり、データビット列を復元できる。

---

## 11。実施内容5：data2.xlsxの複数受信信号合成

### 11.1 目的

`data2.xlsx` に含まれる、2アンテナ、2タイムスロットの合計4つの受信信号を用いて、最適な合成法を検討し、データビット列を復元する。

### 11.2 注意

最初にExcelの列構造を確認すること。各列が以下のどれに対応するかを特定する。

```text
Ant 1、Time slot 1
Ant 1、Time slot 2
Ant 2、Time slot 1
Ant 2、Time slot 2
```

### 11.3 実装内容

- `data2.xlsx` を読み込む。
- 各受信系列についてプリアンブルから伝搬路応答を推定する。
- 各系列を等化する。
- 単一フレームのみを使った復元結果を作る。
- 4つのフレームを合成した復元結果を作る。
- 合成方法として、少なくとも以下を検討する。
  - 単純平均
  - SNRまたは推定伝搬路振幅に基づく重み付き合成
  - スライドのHintに基づく最適重み

### 11.4 合成の基本方針

各アンテナごとに2つのタイムスロット信号を足し、各アンテナの信頼度に応じて重みを付ける。

一般に、伝搬路応答の絶対値が大きいアンテナの方がSNRが高いと考えられるため、重みは `|h|^2` に比例させる方針を候補とする。

### 11.5 出力

```text
outputs/figures/task5/constellation_single_frame.png
outputs/figures/task5/constellation_combined.png
outputs/tables/task5_decoded_bits_single.csv
outputs/tables/task5_decoded_bits_combined.csv
outputs/logs/task5_result.txt
```

必要なら以下も出力する。

```text
outputs/tables/task5_excel_structure.csv
outputs/tables/task5_channel_estimates.csv
outputs/tables/task5_combining_weights.csv
```

### 11.6 レポート下書き

`reports/task5_report.md` を作成し、以下を含める。

- data2.xlsxの構造
- 2アンテナ、2タイムスロットの説明
- 各受信信号の伝搬路応答推定結果
- 単一フレームでの復元結果
- 4フレーム合成での復元結果
- 合成方法の説明
- 単一フレームより4フレーム合成が有利になる理由
- 雑音が独立であるため、合成により雑音成分が平均化されることの考察

### 11.7 考察の方向性

- 4つの受信信号には同じ送信シンボルが含まれているが、雑音は独立である。
- 単一フレームだけを使う場合、雑音やフェージングの影響を強く受ける。
- 複数の受信信号を合成することで、信号成分は強め合い、独立な雑音成分は平均化される。
- SNRが高い受信信号に大きな重みを与えることで、単純平均より高い復元性能が期待できる。
- このような複数受信信号の利用は、ダイバーシティ利得に相当する。

---

## 12。reports/ に作るファイル

以下を作成する。

```text
reports/
├ report_outline.md
├ task1_report.md
├ task2_report.md
├ task3_report.md
├ task4_report.md
├ task5_report.md
├ figures_index.md
└ report_draft.md
```

### 12.1 report_outline.md

実施内容1〜5の構成を示す。

含める内容：

- 各実施内容の目的
- 使用する図表
- 書くべき説明
- 書くべき考察

### 12.2 figures_index.md

レポートに貼る図表の一覧を示す。

例：

```text
図1：QPSK変調波形
貼付元：outputs/figures/task1/qpsk_modulation_waveform.png

図2：QPSK復調波形
貼付元：outputs/figures/task2/qpsk_demodulation_waveform.png

表1：BER理論値と測定値
貼付元：outputs/tables/task3_ber_table.csv
```

### 12.3 report_draft.md

最終レポート本文の下書きとして、実施内容1〜5を統合する。

含める構成例：

```text
# 実験Ⅳ-3 デジタル変復調回路

## 1。目的

## 2。実施内容1：QPSK変調回路

## 3。実施内容2：QPSK復調回路

## 4。実施内容3：熱雑音によるBER評価

## 5。実施内容4：data1.xlsxの復調と伝搬路等化

## 6。実施内容5：data2.xlsxの複数受信信号合成

## 7。まとめ
```

---

## 13。README.md に書く内容

README.mdも更新する。

含める内容：

- 実験名
- 実行環境
- インストール方法
- 実行コマンド
- 出力ファイル一覧
- 提出物の整理方法

実行例：

```bash
python tasks/task1_modulation.py
python tasks/task2_demodulation.py
python tasks/task3_ber.py
python tasks/task4_data1_equalization.py
python tasks/task5_data2_diversity.py
```

---

## 14。requirements.txt

必要に応じて更新する。

想定ライブラリ：

```text
numpy
pandas
matplotlib
scipy
openpyxl
```

---

## 15。.gitignore

以下を含める。

```text
__pycache__/
*.pyc
.venv/
venv/
.ipynb_checkpoints/
.DS_Store
```

outputsをGit管理するかどうかは任意である。  
レポート作成時に図表を追跡したい場合は、outputsをGit管理してもよい。  
ただし、提出用zipやPDFはGit管理しない。

```text
submission/**/*.zip
submission/**/*.pdf
```

---

## 16。提出物の想定

説明ページの指示に従い、最終提出物は以下になる。

### 16.1 レポート

- WordまたはTeXで作成する。
- 実施内容1〜5の実施結果を含める。
- 各実施内容について、説明と考察を含める。
- 図や表を貼り付ける。
- ファイル容量が大きい場合、レポートを分けて投稿する。

### 16.2 ソースコード

- `ipynb`、`py` などのソースコードを一つのZipファイルにまとめる。
- ただし、このリポジトリではPythonスクリプト中心で作る。
- 最終的なzipには、`src/`、`tasks/`、`requirements.txt`、`README.md` を含める。

---

## 17。最初に実行してほしい作業

1. `docs/EIC_Lab4/` 内の参考コードを確認する。
2. `docs/data1.xlsx`、`docs/data2.xlsx` のシート名、列名、先頭行を確認する。
3. Excel構造の確認結果を `outputs/logs/excel_inspection.txt` に保存する。
4. `src/` と `tasks/` に必要なPythonファイルを作成する。
5. 実施内容1から順番に実装する。
6. 各taskを実行して、outputsとreportsを生成する。
7. 最後にREADMEを更新する。

---

## 18。完了条件

以下が満たされれば完了とする。

- `python tasks/task1_modulation.py` が成功する。
- `python tasks/task2_demodulation.py` が成功する。
- `python tasks/task3_ber.py` が成功する。
- `python tasks/task4_data1_equalization.py` が成功する。
- `python tasks/task5_data2_diversity.py` が成功する。
- `outputs/figures/` に実施内容ごとの図が保存されている。
- `outputs/tables/` にBER表と復元ビット列が保存されている。
- `outputs/logs/` に各実施内容の結果ログが保存されている。
- `reports/` に実施内容1〜5の説明と考察下書きが保存されている。
- `reports/figures_index.md` にレポートへ貼る図表一覧がある。
- `reports/report_draft.md` にレポート本文の統合下書きがある。
- `README.md` に実行方法が書かれている。
