# MyATL

競技プログラミングの試験へ持ち込み、必要な実装をファイル／クラス単位で
素早く探してコピーするためのPythonライブラリです。パッケージ機能の多さより、
自己完結性・読みやすさ・正しさ・オフラインでの検索性を優先しています。

## 実装一覧

- `union_find.py`: Union-Find
- `modified_union_find/weighted_union_find.py`: Weighted Union-Find
- `modified_union_find/successor_dsu.py`: Successor DSU
- `fenwick.py`: Fenwick Tree
- `seg_tree.py`: Segment Tree
- `lazy_seg_tree.py`: Lazy Segment Tree
- `scc.py`: Strongly Connected Components
- `max_flow.py`: `MFGraph` / `FlowLowerBound`（最大流・下限付き循環流）
- `trie.py`: Trie
- `rolling_hash.py`: Rolling Hash

旧ファイル名・旧公開名との後方互換は提供しません。上記の正規名を使用して
ください。変更前後の対応はSphinxの「命名変更」に記録しています。

## 規約

ファイル名と関数・メソッドは `snake_case`、クラスは `PascalCase`、定数は
`UPPER_SNAKE_CASE` です。頂点・配列添字は0-indexed、区間は原則として
半開区間 `[left, right)` です。`n` は要素数・頂点数、`m` は辺数を表します。

## テスト

```console
python -m pip install -r requirements-dev.txt
pytest
```

## ドキュメント

```console
python -m pip install -r docs/requirements.txt
python -m sphinx -W -b html docs docs/_build/html
python -m sphinx -W -b doctest docs docs/_build/doctest
```

生成済みHTMLを持ち込む場合は `docs/_build/html/index.html` を開いてください。
ドキュメントソースには用途別早見表、使用ガイド、APIリファレンス、監査記録が
含まれます。NumPyが利用可能な試験環境向けに、密行列演算、行列累乗、法付き演算、
連立一次方程式の注意点をまとめたガイドも収録しています。
