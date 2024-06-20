bot stealer from match

1. Install scapy (pip3 install scapy)
2. Run sniffer_.py (python3 sniffer_.py)
3. Join queue and wait to start match
4. After match, close sniffer_.py and run test.py
5. there should be created BOTNAME.bot file. you can use this for robocraftassember or something...

or
python -m PyInstaller --onefile robocraftStealer.py --add-data "cube_database.csv;."
