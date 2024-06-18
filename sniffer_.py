from scapy.all import *

# 受信するパケットの条件
# cubedata_pattern = b'\x63\x75\x62\x65\x4D\x61\x70\x78\x00\x00'
pattern = b'\x63\x6F\x6C\x6F\x75\x72\x4D\x61\x70\x78'
ip_address = '162.19.204.42'  # 監視するIPアドレス
port = 4541  # 監視するポート番号

flag = 0
f = open("./data", "w")
# パケットを受信して保存する関数
def process_packet(packet):
    global flag
    raw_data = bytes(packet)
    if pattern in raw_data or flag:
        flag = 1
        # パケットを保存する処理（ここでは単純に標準出力に表示）
        data = raw_data.hex()
        f.write(data)

# メインプログラム
if __name__ == "__main__":
    sniff(filter=f"host {ip_address} and port {port}", prn=process_packet, store=0, iface=None, timeout=None)