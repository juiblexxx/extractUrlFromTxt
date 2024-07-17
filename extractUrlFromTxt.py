# coding: utf-8

# 指定したテキストファイルに含まれているURLを別テキストに出力します
# ウィンドウが開いたらbrowseからテキストファイルを選択し
# 実行ボタンを押すと、同じパスに_url.txtファイルが作成されます

# モジュールをインポート
import re
import os
import filecmp
import configparser
import requests

import PySimpleGUI as sg

# ライブラリをインポート
from tkinter import messagebox

config_path = "C:/Data/DL2/Python/extractUrlFromTxt"
config_name = "config.ini"

line_url = ""
line_token = ""

output_file = "urls.txt"
output_old_file = "urls_old.txt"

# 指定したメッセージと画像を貼ってくれるLine通知用の関数
def send_to_line_notify(url:str, token: str, notify_message: str):
    # def send_image_to_line_notify(url: str, token: str, notify_message: str, image_path: str):
    headers = {"Authorization" : "Bearer "+ token}
    # with open(image_path, 'rb') as file:
    #     image = file.read()
    payload = {"message" :  notify_message}
    # files = {"imageFile": image}
    # response = requests.post(url, headers = headers, params=payload, files=files)
    response = requests.post(url, headers=headers, params=payload)
    return response.status_code

def extractUrl(inputpath, reference_text, charset):
    # テキストファイルの存在チェック
    if os.path.isfile(inputpath) :
        pass
    else:
        messagebox.showinfo("ファイルがありません", inputpath)
        return False

    # テキストを開く
    with open(inputpath, "r", encoding=charset) as f:
        # with open(inputpath, "r") as f:
        text = f.read()

    regex = r"https?://[\w/:%#\$&\?\(\)~\.=\+-]+"
    urls = re.findall(regex, text)

    # with open(inputpath + "-url.txt", "w") as w:
    with open(output_file, "a", encoding=charset) as w:
        for url in urls:
            if reference_text != "":
                # 対象文字列指定があった場合は、存在した文字列のみ出力する
                regex = reference_text
                referenceUrl = re.findall(regex, url)
                for rUrl in referenceUrl:
                    w.write(f"{url}\n")
            else:
                w.write(f"{url}\n")

# チェックボックスグループ
CHECKBOX_UTF8 = "-CHECKBOX_UTF8-"
CHECKBOX_CP932 = "-CHECKBOX_CP932-"
CHECKBOX_GID01 = "-CHECKBOX_GID01-"

# ウィンドウに配置する要素を定義
layout = [
    [sg.Text("URLを含んだテキストファイルを指定してください")],
    [sg.InputText(key="url",default_text="C:/Data/DL2/[DL2-irvine]/Siki-win32-x64/data/profile/log/5ch.net/liveuranus/subject.json"), sg.FileBrowse()],
    [sg.Radio("UTF8", key=CHECKBOX_UTF8, group_id=CHECKBOX_GID01, default=True), sg.Radio("CP932", key=CHECKBOX_CP932, group_id=CHECKBOX_GID01)],
    [sg.Text("探したい文字列（URLの一部）があれば指定してください")],
    [sg.InputText(key="reference", default_text="huggin")],
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
        # 比較対象ファイルの削除
        # configparserの宣言とiniファイルの読み込み
        config_ini = configparser.ConfigParser()
        config_ini.read(os.path.join(config_path, config_name), encoding='utf-8')

        # LINE関係の情報をiniから取得
        line_url = config_ini['LINE']['url']
        line_token = config_ini['LINE']['token']

        if os.path.exists(output_old_file) :
            os.remove(output_old_file)

        # 前回結果ファイルをリネーム
        if os.path.exists(output_file) :
            os.rename(output_file, output_old_file)

        filepath = values["url"]    # テキスト入力値を取得
        reference_text = values["reference"] # 探したい文字列を取得

        # 文字コード判定
        charset = "utf-8"
        if values[CHECKBOX_UTF8]:
            charset = "utf-8"
        elif values[CHECKBOX_CP932]:
            charset = "cp932"

        if os.path.isfile(filepath):
            # 振分先ディレクトリパスを作成する為の親パスとして取得しておく
            parent_path = os.path.dirname(filepath)
            # messagebox.showinfo("", parent_path)
            # for file_name in os.listdir(parent_path):
            #     if os.path.isfile(os.path.join(parent_path, file_name)):
            #         print(f"{parent_path}/{file_name}")

            # 同一ディレクトリ内にあるファイルを取得
            files = [os.path.join(parent_path, file_name) for file_name in os.listdir(parent_path) if os.path.isfile(os.path.join(parent_path, file_name))]  # ディレクトリを取得してしまわないようisfileでファイルリストを取取得
            # print(f"{files}")
            # 同一拡張子のファイルのみ検出したいので代表ファイルの拡張子を取得
            base_extention = os.path.splitext(filepath)[1]
            for file in files:
                # 拡張子チェック
                file_extention = os.path.splitext(file)[1]
                if file_extention == base_extention:
                    # messagebox.showinfo("debug", file)
                    extractUrl(file, reference_text, charset)
                    # break   # ループ終了

            # 出力ファイルのdiffとる
            if filecmp.cmp(output_file, output_old_file, shallow=False) == True:
                send_to_line_notify(line_url, line_token, "差分なし")

        # messagebox.showinfo("完了", "出力しました。")
        break
