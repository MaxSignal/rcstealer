from scapy.all import *

import time
import base64
import json
import csv
import os
import sys
import threading
import ctypes

ctypes.windll.kernel32.SetConsoleTitleW("robocraftStealer")

# 受信するパケットの条件
# cubedata_pattern = b'\x63\x75\x62\x65\x4D\x61\x70\x78\x00\x00'
pattern = b'\x63\x6F\x6C\x6F\x75\x72\x4D\x61\x70\x78'
ip_address = '162.19.204.42'  # 監視するIPアドレス
# crf?:4533 singleplayer?:4537 multiplayer?:4541
port = 4541  # 監視するポート番号
conf.bufsize *= 10

data = []
# # パケットを受信して保存する関数
# def process_packet(packet):
#     global data
#     raw_data = bytes(packet)

#     # パケットを保存する処理（ここでは単純に標準出力に表示）
#     data.append(raw_data.hex())

def decimal_to_hex(num):
        # 10進数の数値を16進数文字列に変換する
        h1 = format(num & 0xFF, '02x')
        h2 = format((num >> 8) & 0xFF, '02x')
        h3 = format((num >> 16) & 0xFF, '02x')
        h4 = format((num >> 24) & 0xFF, '02x')
        
        # バイナリデータとして結合する
        data = h1 + h2 + h3 + h4
        
        return data

def packetAnalyser():
    cubeData = []
    displayname = []
    robotNames = []
    name = []
    colourData = []
    ai = []
    ## deleting stupid heartbeats stuff

    f = open("./data", "r")
    data = f.read()

    # ca9637ae89e1e0cec358a6c4080045000028
    tmp = []
    while True:
        idx_start = data.find("ca9637ae89e1e0cec358a6c4080045000028")
        if idx_start == -1:
            break
        data = data[idx_start:]  # 開始インデックスを更新
        idx_end = data.find("e0cec358a6c4ca")
        if idx_end == -1:
            break
        tmp.append(data[:idx_end])  # 終了インデックスまでのデータを追加
        data = data[idx_end:]  # 残りのデータを更新
    f.close()

    f = open("./data", "r")
    rep = f.read()
    f.close()
    f = open("./data", "w")
    for words in tmp:
        rep = rep.replace(words, "")
    f.write(rep)
    f.close()

    f = open("./data", "r")
    data = f.read()

    # ca9637ae89e10800450005 ?
    tmp = []
    while True:
        idx_start = data.find("ca9637ae89e10800450005")
        if idx_start == -1:
            break
        data = data[idx_start:]  # 開始インデックスを更新
        idx_end = 96
        if idx_end == -1:
            break
        tmp.append(data[:idx_end])  # 終了インデックスまでのデータを追加
        data = data[idx_end:]  # 残りのデータを更新
    f.close()

    f = open("./data", "r")
    rep = f.read()
    f.close()
    f = open("./data", "w")
    for words in tmp:
        rep = rep.replace(words, "")
    f.write(rep)
    f.close()

    # e0cec358a6c4
    tmp = []
    tmp.append("e0cec358a6c4")

    f = open("./data", "r")
    rep = f.read()
    f.close()
    f = open("./data", "w")
    for words in tmp:
        rep = rep.replace(words, "")
    f.write(rep)
    f.close()

    ## getting bot info stuff
    f = open("./data", "r")
    data = f.read()

    # 637562654d6170780000 cubeMap
    while True:
        idx_start = data.find("637562654d6170780000")
        if idx_start == -1:
            break
        data = data[idx_start + 24:]  # 開始インデックスを更新
        idx_end = data.find("73000469734149")
        if idx_end == -1:
            break
        cubeData.append(data[:idx_end])  # 終了インデックスまでのデータを追加
        data = data[idx_end:]  # 残りのデータを更新

    f.close()

    if len(cubeData) == 0:
        print("機体データがありません。")
        return

    f = open("./data", "r")
    data = f.read()

    # 726f626f744e616d6573 robotNames
    while True:
        idx_start = data.find("726f626f744e616d6573")
        if idx_start == -1:
            break
        data = data[idx_start + 24:]  # 開始インデックスを更新
        idx_end = data.find("730003")
        if idx_end == -1:
            break
        robotNames.append(data[:idx_end])  # 終了インデックスまでのデータを追加
        data = data[idx_end:]  # 残りのデータを更新

    f.close()

    f = open("./data", "r")
    data = f.read()

    # 646973706c61794e616d6573 displayName
    while True:
        idx_start = data.find("646973706c61794e616d6573")
        if idx_start == -1:
            break
        data = data[idx_start + 28:]  # 開始インデックスを更新
        idx_end = data.find("730007")
        if idx_end == -1:
            break
        displayname.append(data[:idx_end])  # 終了インデックスまでのデータを追加
        data = data[idx_end:]  # 残りのデータを更新

    f.close()

    f = open("./data", "r")
    data = f.read()

    # 6e616d6573 name
    while True:
        idx_start = data.find("046e616d6573")
        if idx_start == -1:
            break
        data = data[idx_start + 16:]  # 開始インデックスを更新
        idx_end = data.find("7300")
        if idx_end == -1:
            break
        name.append(data[:idx_end])  # 終了インデックスまでのデータを追加
        data = data[idx_end:]  # 残りのデータを更新

    f.close()

    f = open("./data", "r")
    data = f.read()

    # 73000469734149 colourMap
    # 9636f6c6f75724d6170780000
    while True:
        idx_start = data.find("09636f6c6f75724d6170780000")
        if idx_start == -1:
            break
        data = data[idx_start + 30:]  # 開始インデックスを更新
        idx_end = data.find("7300")
        if idx_end == -1:
            break
        colourData.append(data[:idx_end])  # 終了インデックスまでのデータを追加
        data = data[idx_end:]  # 残りのデータを更新

    f.close()

    f = open("./data", "r")
    data = f.read()

    #isAI
    while True:
        idx_start = data.find("69734149")
        if idx_start == -1:
            break
        data = data[idx_start + 10:]  # 開始インデックスを更新
        if data[:2] == "00":
            ai.append(False)
        else:
            ai.append(True)
        data = data[2:]

    f.close()
    
    cubeDatabase = {}
    csv_file_path = os.path.join(sys._MEIPASS, 'cube_database.csv')
    with open(csv_file_path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[1].isdecimal():
                cubeDatabase[decimal_to_hex(int(row[1]))] = int(row[1]) 

    if not os.path.exists("./bots"):
        os.makedirs("./bots")
        os.makedirs("./bots/AI")
    elif not os.path.exists("./bots/AIs"):
        os.makedirs("./bots/AIs")

    print("総機体数: " + str(len(cubeData)))
    for i in range(len(cubeData)):
        if ai[i]:
            f = open("./bots/AIs/" + bytes.fromhex(displayname[i]).decode(encoding='utf-8') + "_" + str(int(time.time())) + ".bot", "w")
        else:
            f = open("./bots/" + bytes.fromhex(displayname[i]).decode(encoding='utf-8') + "_" + str(int(time.time())) + ".bot", "w")
        cubes = {}
        for cube in cubeDatabase.keys():
            if cube in cubeData[i]:
                cubes[cubeDatabase[cube]] = str(cubeData[i]).count(cube)

        if ai[i]:
            print("Save " + bytes.fromhex(robotNames[i]).decode(encoding='utf-8') + " by " + \
                bytes.fromhex(displayname[i]).decode(encoding="utf-8") + "(AI) as " + \
                    bytes.fromhex(displayname[i]).decode(encoding='utf-8') + "_" + str(int(time.time())) +".bot")
        else:
            print("Save " + bytes.fromhex(robotNames[i]).decode(encoding='utf-8') + " by " + \
                bytes.fromhex(displayname[i]).decode(encoding="utf-8") + " as " + \
                    bytes.fromhex(displayname[i]).decode(encoding='utf-8') + "_" + str(int(time.time())) +".bot")

        # JSONデータを作成
        data = {
            "id": 0,
            "name": bytes.fromhex(robotNames[i]).decode(encoding='utf-8'),
            "description": "",
            "thumbnail": "",
            "addedBy": bytes.fromhex(name[i]).decode(encoding="utf-8"),
            "addedByDisplayName": bytes.fromhex(displayname[i]).decode(encoding="utf-8"),
            "addedDate": "",
            "expiryDate": "",
            "cpu": 0,
            "totalRobotRanking": 0,
            "buyable": False,
            "rentCount": 0,
            "buyCount": 0,
            "combatRating": 0.0,
            "cosmeticRating": 0.0,
            "cubeData": base64.b64encode(bytes.fromhex(cubeData[i])).decode(),
            "colourData": base64.b64encode(bytes.fromhex(colourData[i])).decode(),
            "featured": False,
            "bannerMessage": "",
            "cubeAmounts": cubes
        }

        # JSONを文字列に変換
        json_string = json.dumps(data, indent=4)
        f.write(json_string)
        f.close()

def start_sniffing():
    global data
    sniff(filter=f"tcp and src host {ip_address} and src port {port}", prn=lambda pkts: data.append(pkts), count=0, store=0, iface=None, timeout=None)

# メインプログラム
def main():
    print("起動中...")
    sniff_thread = threading.Thread(target=start_sniffing)
    sniff_thread.daemon = True
    sniff_thread.start()

    idx = 0
    print("パケット監視中...")
    print("終了するときはCtrl+Cを押してください... ")
        
    try:
        while(1):
            time.sleep(1)
            combinedData = []
            for pkts in data:
                combinedData.append(bytes(pkts).hex())
            combinedData = ''.join(combinedData)

            #ユーザ名があるか確認(最後の行なので)
            idx_start = combinedData[idx:].rfind("046e616d6573")
            if idx_start == -1:
                continue

            idx_start = idx + idx_start + 16
            idx_end = combinedData[idx_start:].find("7300")
            if idx_end == -1:
                continue

            idx_end = idx_start + idx_end + 4
            # print(combinedData[idx_start:idx_end]) debug

            oidx = idx
            idx = idx_end  # データの最後
            
            f = open("./data", "w")
            f.write(combinedData[oidx:idx])
            f.close()

            packetAnalyser()
    except KeyboardInterrupt:        
        while(1):
            save = input("パケットデータ(通常は不要)を保存しますか? Yes:[y] No:[n] > ")
            if save == "y":
                combinedData = []
                for pkts in data:
                    combinedData.append(bytes(pkts).hex())
                combinedData = ''.join(combinedData)

                f = open("./data", "w")
                f.write(combinedData)
                f.close()
                os.rename("./data", "./data-" + str(int(time.time())))
                break
            elif save == "n":
                os.remove('./data')
                break
            else:
                print("yかnを入力してください")
                
        return

if __name__ == "__main__":
    main()
    
    sys.exit(1)