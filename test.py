import base64
import json

import csv
cubeData = []
displayname = []
robotNames = []
name = []
colourData = []

def decimal_to_hex(num):
        # 10進数の数値を16進数文字列に変換する
        h1 = format(num & 0xFF, '02x')
        h2 = format((num >> 8) & 0xFF, '02x')
        h3 = format((num >> 16) & 0xFF, '02x')
        h4 = format((num >> 24) & 0xFF, '02x')
        
        # バイナリデータとして結合する
        data = h1 + h2 + h3 + h4
        
        return data

f = open("data", "r")
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

f = open("data", "r")
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

f = open("data", "r")
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

f = open("data", "r")
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

f = open("data", "r")
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

cubeDatabase = {}
with open("cube_database.csv", "r") as f:
    reader = csv.reader(f)
    for row in reader:
        if row[1].isdecimal():
            cubeDatabase[decimal_to_hex(int(row[1]))] = int(row[1]) 

for i in range(len(cubeData)):
    f = open("bots/" + bytes.fromhex(robotNames[i]).decode(encoding='utf-8') + ".bot", "w")

    cubes = {}
    for cube in cubeDatabase.keys():
        if cube in cubeData[i]:
            cubes[cubeDatabase[cube]] = str(cubeData[i]).count(cube)

    # JSONデータを作成
    data = {
        "id": 0,
        "name": bytes.fromhex(robotNames[i]).decode(encoding='utf-8'),
        "description": "",
        "thumbnail": "",
        "addedBy": bytes.fromhex(name[i]).decode(encoding='utf-8'),
        "addedByDisplayName": bytes.fromhex(displayname[i]).decode(encoding='utf-8'),
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