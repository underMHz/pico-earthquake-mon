# pico-earthquake-mon

Raspberry Pi Pico Wを使って「地震情報をリアルタイム」で表示するインフォメーションモニタです。

地震情報は「P2P地震情報」が提供しているWebSocketで取得しています。

[P2P地震情報 - Wikipedia](https://ja.wikipedia.org/wiki/P2P%E5%9C%B0%E9%9C%87%E6%83%85%E5%A0%B1)

地震情報は、震源地・地震の深さ・発生日時・震度・規模の5つがOLED（128×32）に表示されます。

揺れを取得した都道府県は基板上の各LEDに対応しており、揺れた都道府県に対応したLEDが点灯します。

リチウムイオン電池（18650）を使うので、スタンドアロンで使用できます。

----

## 開発環境

・MicroPython(v1.22.2)

・Thonny(v4.0.2)

----

## 動作の様子

![動作](img/example.gif)

実際の動作の様子です。

受信する地震情報についてはリアルタイムのものではなくダミー用に表示しているものです。

土台は3Dプリンタ（光造形）で作製しています。

STLファイルは[case.stl](https://github.com/underMHz/pico-info-mon/blob/main/case.stl)にあります。

----


## 部品リスト

|部品名|個数|購入先リンク|注意|
|:--|:--|:--|:--|
|メイン基板|1||BOOTHに出品予定？|
|Raspberry Pi Pico W|1|https://akizukidenshi.com/catalog/g/g117947/||
|タクトスイッチ|1|https://akizukidenshi.com/catalog/g/g103646/|Pi Picoリセット用。色はなんでもよい|
|TP4056 リチウム電池充電モジュール|1|https://amzn.asia/d/iQMhM1q|Amazon等に出回っている汎用充電モジュール|
|XHコネクタ メス|2|https://akizukidenshi.com/catalog/g/g112247/||
|XHコネクタ オス|1-2|https://akizukidenshi.com/catalog/g/g112255/||
|XHコネクタ コンタクト|2|https://akizukidenshi.com/catalog/g/g112264/||
|リチウム電池（18650）電池ボックス|1|https://akizukidenshi.com/catalog/g/g108407/||
|電線|適宜|https://akizukidenshi.com/catalog/g/g110672/||
|ショットキーバリアダイオードSB240LES|1|https://akizukidenshi.com/catalog/g/g107787/||
|コンデンサ 0.15uF 50V|6|https://akizukidenshi.com/catalog/g/g108145/|バイパスコンデンサ。タンタルコンデンサが好ましい|
|TC74HC595AF|6|https://akizukidenshi.com/catalog/g/g110077/|8bitシフトレジスタ|
|緑色チップLED 1608|49|https://akizukidenshi.com/catalog/g/g111878/||
|チップ抵抗 1/10W 3kΩ|49|https://akizukidenshi.com/catalog/g/g106302/|眩しいため6kΩ程度が望ましい|
|細ピンヘッダ|20*2 4 6|https://akizukidenshi.com/catalog/g/g104398/|Pi Pico固定用とOLED固定用とTP4056モジュール固定用|
|M3×35ボルト|2||基板立て用。長さは35mmでなくてもよい|
|M3ナット|2||基板立て用|
|はんだ|適宜||はんだ用|

----

## ブロック図

（工事中🔨）

----

## 回路図

（工事中🔨）

----

## ガーバーデータ（基板発注のためのデータ）

（工事中🔨）

![ピンアサイン](img/picow_pin.png)

----

## 接続

（工事中🔨）

![ピンアサイン](img/picow_pin.png)

----

## ファイル構成

- ThonnyからPython Package Index(PyPI)からインストールするライブラリ

`hogehoge`

`hogehoge`

- 外部でインストールしてから追加するライブラリ

`hogehoge`
https://github.com/hogehoge/hogehoge/blob/master/hogehoge.py

- 使用するフォント

`misakifont`（美咲フォント）
https://github.com/Tamakichi/pico_MicroPython_misakifont/tree/main/misakifont

❓美咲フォントについて
https://littlelimit.net/misaki.htm

（工事中🔨）
        
----
