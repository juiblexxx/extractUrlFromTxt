# coding: utf-8

# 指定したテキストファイルに含まれているURLを別テキストに出力します
# ウィンドウが開いたらbrowseからテキストファイルを選択し
# 実行ボタンを押すと、同じパスに_url.txtファイルが作成されます

import re
import os
import filecmp
import configparser
import requests
import PySimpleGUI as sg
from tkinter import messagebox

# 規定値の定義
config_path = os.path.join(os.path.dirname(__file__), 'config.ini')



def send_to_line_notify(url:str, token: str, notify_message: str):
    # def send_image_to_line_notify(url: str, token: str, notify_message: str, image_path: str):
    # 指定したメッセージと画像を貼ってくれるLine通知用の関数
    headers = {"Authorization" : "Bearer "+ token}
    # with open(image_path, 'rb') as file:
    #     image = file.read()
    payload = {"message" :  notify_message}
    # files = {"imageFile": image}
    # response = requests.post(url, headers = headers, params=payload, files=files)
    response = requests.post(url, headers=headers, params=payload)
    return response.status_code



def extract_url(input_path, charset) -> str:
    # input_pathからURL文字列のみを返す
    # ファイルを開く
    with open(input_path, "r", encoding = charset) as f:
        text = f.read()

    regex = r"https?://[\w/:%#\$&\?\(\)~\.=\+-]+"   # URL用の正規表現
    return re.findall(regex, text)



def main_gui(target_path, target_string):
    # チェックボックスグループの定義
    CHECKBOX_UTF8 = "-CHECKBOX_UTF8-"
    CHECKBOX_CP932 = "-CHECKBOX_CP932-"
    CHECKBOX_GID01 = "-CHECKBOX_GID01-"

    # PySimpleGUIウィンドウに配置する要素を定義
    layout = [
        [sg.Text("チェックしたいファイルを指定してください。\n同じフォルダで同じ拡張子をもつファイルをチェック対象とします。\nカンマ区切りで複数指定可")],
        [sg.InputText(key="paths",default_text=target_path), sg.FileBrowse()],
        [sg.Radio("UTF-8", key=CHECKBOX_UTF8, group_id=CHECKBOX_GID01, default=True), sg.Radio("CP932", key=CHECKBOX_CP932, group_id=CHECKBOX_GID01)],
        [sg.Text("探したい文字列（URLの一部）があれば指定してください\nカンマ区切りで複数指定可")],
        [sg.InputText(key="references", default_text=target_string)],
        [sg.Button("実行")]
    ]

    # PySimpleGUIウィンドウを生成
    window = sg.Window("extractUrlFromTxt", layout)

    # UIループ
    while True:
        event, values = window.read()    # イベントと入力値を取得
        if event == sg.WIN_CLOSED:  # ウィンドウが閉じられたら
            break   # UIループ終了

        elif event == "実行":   # 実行ボタンが押されたら
            if values[CHECKBOX_UTF8]:
                target_charset = "utf-8"
            elif values[CHECKBOX_CP932]:
                target_charset = "cp932"

            main(values["paths"], values["references"], target_charset)
            messagebox.showinfo("完了", "処理完了しました。")
            break   # UIループ終了



def main(target_path, target_string, target_charset):
    # メイン処理
    # 古い前回結果ファイルを削除
    if os.path.exists(output_old_file):
        os.remove(output_old_file)

    # 前回結果ファイルをリネーム
    if os.path.exists(output_file) :
        os.rename(output_file, output_old_file)

    # チェック対象ファイルの文字コードセット
    charset = target_charset

    # チェック処理開始
    for file_path in target_path.split(","):
        if os.path.isfile(file_path):
            # 基準拡張子とカレントパスを取得
            base_extention = os.path.splitext(file_path)[1]
            parent_path = os.path.dirname(file_path)

            # ディレクトリを取得してしまわないようisfileでファイルのみ取得
            # かつ、base_extentionと同一拡張子のみ
            # endswithでチェックするので大文字・小文字の区別あり
            files = [
                os.path.join(parent_path, file_name)
                for file_name in os.listdir(parent_path)
                if os.path.isfile(os.path.join(parent_path, file_name)) and file_name.endswith(base_extention)
                ]
            # files は parent_path + file_name
            # file_name は parent_path の listdir
            # 但し、parent_path + parent_name がファイル かつ 拡張子が base_extention なら

            with open(output_file, "a", encoding = charset) as w:
                # 見つかったファイルからURL文字列を取得する
                # URLの絞り込み指定があったなら、絞り込んだURLのみファイルに出力する
                for file in files:
                    urls = extract_url(file, charset)
                    for url in urls:
                        if target_string != "":
                            # 対象文字列指定があった場合は、存在した文字列のみ出力する
                            for regex in target_string.split(","):
                                reference_url = re.findall(regex, url)
                                for ret in reference_url:   # ここでマッチした箇所は無視、元URLを出力したい
                                    w.write(f"{url}\n")
                        else:
                            w.write(f"{url}\n")

    # 出力ファイルのdiffとる
    if filecmp.cmp(output_file, output_old_file, shallow = False) == False and line_enable == "1":
        with open(output_file, "r", encoding = charset) as f:
            # リストから最後の要素を取得
            last_line = f.readlines()[-1].rstrip("\n")
        # print (f"{last_line}")
        send_to_line_notify(line_url, line_token, f"差分あり：{last_line}")



# コンフィグの取得
config_ini = configparser.ConfigParser()
config_ini.read(config_path, encoding="utf-8")

# コンフィグ値を変数に代入しておく
gui = config_ini["SETTINGS"]["gui"]
output_file = config_ini["SETTINGS"]["output_new"]
output_old_file = config_ini["SETTINGS"]["output_old"]
target_path = config_ini["SETTINGS"]["target_path"]
target_string = config_ini["SETTINGS"]["target_string"]
target_charset = config_ini["SETTINGS"]["target_charset"]
line_enable = config_ini["LINE"]["enable"]
line_url = config_ini["LINE"]["url"]
line_token = config_ini["LINE"]["token"]



if __name__ == "__main__":
    if gui == "1":
        main_gui(target_path, target_string)
    else:
        main(target_path, target_string, target_charset)

