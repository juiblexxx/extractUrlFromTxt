# coding: utf-8

# 指定したテキストファイルに含まれているURLを別テキストに出力します
# ウィンドウが開いたらbrowseからテキストファイルを選択し
# 実行ボタンを押すと、同じパスに_url.txtファイルが作成されます

# モジュールをインポート
import re
import os
import PySimpleGUI as sg

# ライブラリをインポート
from tkinter import messagebox

def extractUrl(inputpath):
    # テキストファイルの存在チェック
    if os.path.isfile(inputpath) :
        pass
    else:
        messagebox.showinfo("ファイルがありません", inputpath)
        return False

    # テキストを開く
    with open(inputpath, "r") as f:
        text = f.read()

    regex = r"https?://[\w/:%#\$&\?\(\)~\.=\+-]+"

    urls = re.findall(regex, text)

    with open(inputpath + "-url.txt", "w") as w:
        for url in urls:
            w.write(f"{url}\n")

# ウィンドウに配置する要素を定義
layout = [
    [sg.Text("URLを含んだテキストファイルを指定してください")],
    [sg.InputText(key="url"), sg.FileBrowse()],
    [sg.Button("実行")]
]

# ウィンドウを作成
window = sg.Window("extractUrlFromTxt", layout)

# イベントループ
while True:
    event, values = window.read()    # イベントと入力値を取得
    if event == sg.WIN_CLOSED:  # ウィンドウが閉じられたら
        break   # ループ終了
    elif event == "実行":   # 実行ボタンが押されたら
        filepath = values["url"]    # テキスト入力値を取得
        extractUrl(filepath)
        messagebox.showinfo("完了", "出力しました。")
        break

