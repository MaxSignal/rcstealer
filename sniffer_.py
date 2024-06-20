from scapy.all import *
import time

# 受信するパケットの条件
# cubedata_pattern = b'\x63\x75\x62\x65\x4D\x61\x70\x78\x00\x00'
pattern = b'\x63\x6F\x6C\x6F\x75\x72\x4D\x61\x70\x78'
ip_address = '162.19.204.42'  # 監視するIPアドレス
# crf?:4533 singleplayer?:4537 multiplayer?:4541
port = 4541  # 監視するポート番号

data = ""
# パケットを受信して保存する関数
def process_packet(packet):
    global data
    raw_data = bytes(packet)

    # パケットを保存する処理（ここでは単純に標準出力に表示）
    data += str(raw_data.hex())

# メインプログラム
if __name__ == "__main__":
    try:
        t = AsyncSniffer(filter=f"host {ip_address} and port {port}", prn=process_packet, store=0, iface=None, timeout=None)
        t.start()
        print("パケット監視中...")
        print("終了時はCtrl+Cを押してください")
        while(1):
            pass
    except:
        t.stop()
        print("data: " + data)
        f = open("data", "w")
        f.write(data)
        f.close()