from lib.blender import Blender
from lib.parser import Parser

import os
import glob
import ctypes
import sys
import __future__

ctypes.windll.kernel32.SetConsoleTitleW("robocraftStealer")

class BlendExpoter:
    def __init__(self):
        self.blender = Blender()
        self.parser = Parser()
        self.csv_file_path = os.path.join(sys._MEIPASS, 'assets/cubes.csv')
    
    def export(self, filename, savepath):
        self.blender.unselectEverything()
        self.cubeData = self.parser.parseBotFile(savepath)
        self.cubedatabase = self.parser.parseCSVFile(self.csv_file_path)
        self.blender.export(str(filename), self.cubeData, self.cubedatabase)

    def exportfbx(self, filename, savepath):
        self.blender.unselectEverything()
        self.cubeData = self.parser.parseBotFile(savepath)
        self.cubedatabase = self.parser.parseCSVFile(self.csv_file_path)
        self.blender.export_fbx(str(filename), self.cubeData, self.cubedatabase)
    
    def exportx3d(self, filename, savepath):
        self.blender.unselectEverything()
        self.cubeData = self.parser.parseBotFile(savepath)
        self.cubedatabase = self.parser.parseCSVFile(self.csv_file_path)
        self.blender.export_x3d(str(filename), self.cubeData, self.cubedatabase)
    
    def exportgltf(self, filename, savepath):
        self.blender.unselectEverything()
        self.cubeData = self.parser.parseBotFile(savepath)
        self.cubedatabase = self.parser.parseCSVFile(self.csv_file_path)
        self.blender.export_gltf(str(filename), self.cubeData, self.cubedatabase)
    
    def exportstl(self, filename, savepath):
        self.blender.unselectEverything()
        self.cubeData = self.parser.parseBotFile(savepath)
        self.cubedatabase = self.parser.parseCSVFile(self.csv_file_path)
        self.blender.export_stl(str(filename), self.cubeData, self.cubedatabase)

def main():
    os.system('cls')

    expoter = BlendExpoter()
    if not os.path.exists("./bots"):
        os.makedirs("./bots")
    if not os.path.exists("./converted"):
        os.makedirs("./converted")
    l = glob.glob('./bots/*.bot')
    if len(l) == 0:
        print("機体ファイル(.bot)をbotsフォルダに入れてください")
        return
    
    botName = []
    created = []
    cubeData = []
    colourData = []
    filename = []
    for file in l:
        print(file)
        with open(file, 'r', encoding='utf-8') as f:
            data = f.read().replace("false", "False").replace("true", "True")
            botData =  eval(data)
        botName.append(botData["name"])
        created.append(botData["addedByDisplayName"])
        cubeData.append(botData["cubeData"])
        colourData.append(botData["colourData"])
        filename.append(os.path.basename(file)[:-4])
    while(1):
        u = input("変換したいフォーマットを選択: blend, fbx, x3d, gltf, stl > ")
        if u in ["blend", "fbx", "x3d", "gltf", "stl"]:
            break
        print("正しいフォーマットを入力してください")
    
    print("変換開始(これには時間がかかります...)")
    base = "./converted/"
    for i in range(len(l)):
        print("Convert " + botName[i] + " by " + created[i] + " to " + u + " format...")
        if u == "fbx":
            expoter.exportfbx(base + filename[i], l[i])
        elif u == "x3d":
            expoter.exportx3d(base + filename[i], l[i])
        elif u == "gltf":
            expoter.exportgltf(base + filename[i], l[i])
        elif u == "stl":
            expoter.exportstl(base + filename[i], l[i])
        elif u == "blend":
            expoter.export(base + filename[i], l[i])
    
    print("変換完了")

    return
    
main()
sys.exit(0)