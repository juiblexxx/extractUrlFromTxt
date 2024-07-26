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



def send_to_line_notify(url:str, token: str, notify_message: str) -> int:
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



def extract_url(input_path, charset) -> list:
    # ファイルを開いてURLだけをリスト化して返す
    with open(input_path, "r", encoding = charset) as f:
        text = f.read() # ファイルの中身全部読む
    regex = r"https?://[\w/:%#\$&\?\(\)~\.=\+-]+"   # URL用の正規表現
    return re.findall(regex, text) # リストで戻す



def matches_any_pattern(text: str, patterns: str) -> bool:
    """
    テキストが複数の正規表現パターンのいずれかにマッチするかをチェックする関数。
    :param text: 検索対象の文字列
    :param patterns: 正規表現パターンのリスト
    :return: マッチした場合は True、そうでない場合は False
    """
    for pattern in patterns:
        if re.search(pattern, text):
            return True
    return False

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
    for file_path in target_path.split(","):    # カンマで区切って複数パスを全部処理する
        if os.path.isfile(file_path) == False:  # ファイルじゃなければ次の指定パスへ
            continue

        # 基準拡張子とカレントパスを取得
        base_extention = os.path.splitext(file_path)[1]
        parent_path = os.path.dirname(file_path)

        # ディレクトリを取得してしまわないようisfileでファイルのみ取得
        # かつ、base_extentionと同一拡張子のみ
        files = [
            os.path.join(parent_path, file_name)
            for file_name in os.listdir(parent_path)
            if os.path.isfile(os.path.join(parent_path, file_name)) and file_name.lower().endswith(base_extention.lower())
            ]
        # files は parent_path + file_name
        # file_name は parent_path の listdir
        # 但し、parent_path + parent_name がファイル かつ 拡張子が base_extention なら
        # endswithでチェックするので大文字・小文字の区別あり（よって小文字にして比較する）

        # 見つかったファイルからURL文字列を取得しファイルに出力
        # URLの絞り込み指定target_stringがあったなら、絞り込んだURLのみファイルに出力する
        with open(output_file, "a", encoding = charset) as w:
            url_prev = "" # 連続して同じURLは出力しないチェック用
            for file in files:  # 入力パスから取得したファイル群を1づつ処理していく
                urls = extract_url(file, charset)   # ファイル内のURLをリストで取得
                for url in urls:
                    # 前と同じURLはそもそもチェックしない
                    if url_prev == url:
                        continue
                    url_prev = url

                    # URLの絞り込みがあれば、マッチするかチェック
                    # マッチなければ出力せず次へ
                    if target_string != "" and matches_any_pattern(url, target_string.split(",")) == False:
                        continue

                    w.write(f"{url}\n")
                    url_prev = url  # 間をおいて同じURLがある可能性があるので、ここでも入れなおす

    # 出力ファイルのdiffとる
    if filecmp.cmp(output_file, output_old_file, shallow = False) == False and line_enable == "1":
        with open(output_file, "r", encoding = charset) as f:
            # リストから最後の要素を取得
            last_line = f.readlines()[-1].rstrip("\n")
        send_to_line_notify(line_url, line_token, f"差分あり：{last_line}")



# コンフィグの取得
config_ini = configparser.ConfigParser()
config_ini.read(config_path, encoding="utf-8")

# コンフィグ値を変数に代入しておく
gui = config_ini["SETTINGS"].get("gui", "1")
output_file = config_ini["SETTINGS"].get("output_new", "_url.txt")
output_old_file = config_ini["SETTINGS"].get("output_old", "_url_old.txt")
target_path = config_ini["SETTINGS"].get("target_path", "./")
target_string = config_ini["SETTINGS"].get("target_string", "")
target_charset = config_ini["SETTINGS"].get("target_charset", "utf8")
line_enable = config_ini["LINE"].get("enable", "0")
line_url = config_ini["LINE"].get("url", "")
line_token = config_ini["LINE"].get("token", "")



if __name__ == "__main__":
    if gui == "1":
        main_gui(target_path, target_string)
    else:
        main(target_path, target_string, target_charset)

