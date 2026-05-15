# 実験IV-3 デジタル変復調回路

QPSK変復調、AWGN環境でのBER測定、プリアンブルを用いた伝搬路推定、ダイバーシチ合成をPythonで実装する作業用リポジトリです。

## 実行方法

リポジトリルートで以下を実行します。

```bash
python3 tasks/task1_qpsk_modulation.py
python3 tasks/task2_qpsk_demodulation.py
python3 tasks/task3_ber_awgn.py
python3 tasks/task4_data1_equalization.py
python3 tasks/task5_data2_diversity.py
```

## 出力

- 図: `outputs/figures/`
- 表: `outputs/tables/`
- ログ: `outputs/logs/`
- レポート下書き: `reports/`

`docs/EIC_Lab4/` は参考コード置き場として扱い、実装は `src/` と `tasks/` に分離しています。
