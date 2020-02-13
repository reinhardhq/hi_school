ハイスクール
====

Overview

## Description
* 学校名を入力にみんなの高校情報(https://www.minkou.jp/)の検索を行い検索結果1件目の学校詳細を返却します。

## Requirement

* packages.txt


## Usage

* INPUT:
    * String

* OUTPUT:
    * List
        * '入力高校名'
        * '学校名'
        * '都道府県'
        * '市区町村'
        * '公立・私立'
        * '共学・男子校・女子校'
        * '偏差値'
        * 'ランキングタイトル'
        * 'ランキング分子'
        * 'ランキング分母'
        * '県内公立・私立ランキングタイトル'
        * 'ランキング分子'
        * 'ランキング分母'
        * '全国ランキングタイトル'
        * 'ランキング分子'
        * 'ランキング分母'

* Exception
    * 学校が存在しない場合以下の例外を返却
        * assets.hischool.NotFoundException

* テストファイル

```bash
# python test.py
```

## Contribution

## Licence

* pass

## Author

* pass
