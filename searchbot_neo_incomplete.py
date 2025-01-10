import csv
import json
import asyncio
import aiohttp
import sqlite3

import discord
from discord import app_commands
from discord.ext import tasks
from rcapi import factory

DB_PATH = "bots.db"

# BOTのトークン
TOKEN = ""

# BIG-MRTのトークン
WEBHOOK_URL = ""

# CRF API用のトークン
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJQdWJsaWNJZCI6IjEyMyIsIkRpc3BsYXlOYW1lIjoiVGVzdCIsIlJvYm9jcmFmdE5hbWUiOiJGYWtlQ1JGVXNlciIsIkZsYWdzIjpbXSwiaXNzIjoiRnJlZWphbSIsInN1YiI6IldlYiIsImlhdCI6MTU0NTIyMzczMiwiZXhwIjoyNTQ1MjIzNzkyfQ.ralLmxdMK9rVKPZxGng8luRIdbTflJ4YMJcd25dKlqg"

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
loop_lock = asyncio.Lock()

#SQL検索
def search_data(sqlite_db, query):
    # SQLite3データベースに接続
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()

    # クエリの実行
    cursor.execute(query)

    # 結果の取得
    results = cursor.fetchall()

    # 接続をクローズ
    conn.close()

    # 結果の表示
    return results

##SQL挿入
def insert_data_to_sqlite(json_file, sqlite_db):
    # SQLite3データベースに接続
    conn = sqlite3.connect(sqlite_db)
    cursor = conn.cursor()

    # テーブル作成
    create_table_query = '''
        CREATE TABLE IF NOT EXISTS bots (
            id INTEGER PRIMARY KEY,
            name TEXT,
            description TEXT,
            thumbnail TEXT,
            addedBy TEXT,
            addedByDisplayName TEXT,
            addedDate TEXT,
            expiryDate TEXT,
            cpu INTEGER,
            totalRobotRanking INTEGER,
            rentCount INTEGER,
            buyCount INTEGER,
            combatRating REAL,
            cosmeticRating REAL,
            featured BOOLEAN,
            cubeAmounts TEXT
        )
    '''
    cursor.execute(create_table_query)

    # JSONファイルからデータ読み込み
    with open(json_file, 'r', encoding='utf-8') as jsonfile:
        data = json.load(jsonfile)

    # データ挿入
    cursor.execute('''
        INSERT INTO bots VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (int(data["id"]), data["name"], data["description"], data["thumbnail"], data["addedBy"],
          data["addedByDisplayName"], data["addedDate"], data["expiryDate"], int(data["cpu"]),
          int(data["totalRobotRanking"]), int(data["rentCount"]), int(data["buyCount"]), float(data["combatRating"]),
          float(data["cosmeticRating"]), bool(data["featured"]), data["cubeAmounts"]))

    # コミットしてクローズ
    conn.commit()
    conn.close()

#BOTダウンロード
def download_bot(token, bot_id):
    bot_info = factory.factory_bot(token, bot_id)
    save_path = f"./bots-7800000/{bot_info['id']}.bot"
    print(f'Downloading {bot_info["name"]} to {save_path}...')
    with open(save_path, 'wb') as f:
        f.write(json.dumps(bot_info, indent=4).encode('utf-8'))

#CRFクローラー
def crawler():
    last = search_data(DB_PATH, "SELECT id FROM bots ORDER BY id DESC LIMIT 1;")[0][0]

    max_failed_attempts = 5
    count_bot = 1       
    failed_attempts = 0
    new = []

    #5回失敗するまでbotを取得
    while True:
        try:
            download_bot(token, last + count_bot)
            new.append(last + count_bot)
            count_bot += 1
            failed_attempts = 0  # 成功した場合は失敗カウントをリセット
        except Exception as e:
            failed_attempts += 1
            if failed_attempts >= max_failed_attempts:
                # print(f"Reached {max_failed_attempts} consecutive failures. Exiting.")
                break

    #DBに保存
    if count_bot > 1:
        for bot_id in new:
            try:
                # SQLite3データベースに挿入
                insert_data_to_sqlite(f"./bots-7800000/{bot_id}.bot", DB_PATH)

            except Exception as e:
                print(f"Error processing {bot_id}.bot: {e}")
    else:
        return []

    result = search_data(DB_PATH, "SELECT * FROM bots WHERE id >= " + str(last + 1))

    data_name = []
    data = []
    f = open("./essential_cubes.csv", "r")
    reader = csv.reader(f)

    for row in reader:
        if row[2].isdecimal() and not int(row[2]) in data:
            data_name.append(row[1])
            data.append(int(row[2]))

    f.close()
    
    for i in range(len(result)):

        if result[i][8] > 2000:
            _tier = "TM"
        elif result[i][9] <= 1000:
            _tier = 1
        elif result[i][9] <= 6434:
            _tier = 2
        elif result[i][9] <= 79999:
            _tier = 3
        elif result[i][9] <= 1299999:
            _tier = 4
        else:
            _tier = 5

        cubelist = ""
        cubedata = json.loads(result[i][15])
        keys = list(cubedata.keys())
        for k in range(len(data)):
            for j in range(len(cubedata)):

                if data[k] == int(keys[j]):
                    cubelist += data_name[k] + ": " + str(cubedata[keys[j]]) + "\n"

        # img = Image.open(io.BytesIO(requests.get(result[i][3]).content))
        # (width, height) = (img.width * 1.25, img.height * 1.25)
        # img_resized = img.resize((width, height))
        # file = discord.File(img_resized, filename="image.png")
        # embed.set_image(url="attachment://image.png")

        embeds = []            
        embeds.append(discord.Embed(title="機体情報"))
        embeds[i].add_field(name="機体名",value=result[i][1],inline=False)
        embeds[i].add_field(name="作者",value=result[i][4] + " aka " + result[i][5],inline=False)
        embeds[i].add_field(name="CPU",value=result[i][8],inline=False)
        embeds[i].add_field(name="ティア",value=str(_tier),inline=False)
        embeds[i].add_field(name="機体説明",value=result[i][2],inline=False)

        if len(cubelist) > 768:
            embeds[i].add_field(name="使用パーツ",value="使用パーツ過多のため省略",inline=False)
        else:
            embeds[i].add_field(name="使用パーツ",value=cubelist,inline=False)

        embeds[i].add_field(name="出品期限",value=result[i][7],inline=False)
        embeds[i].set_footer(text="ID: " + str(result[i][0]) + " • " + result[i][6])
        embeds[i].set_image(url=result[i][3])
    
    n = 10
    result = [embeds[idx:idx + n] for idx in range(0,len(embeds), n)]
    return result

def search_bots(enable_robot_id, 
                enable_creator_id, 
                enable_nick_name, 
                enable_name, 
                enable_description,
                enable_cpu,
                enable_buy_count,
                enable_battlle_count,
                enable_featured,
                enable_tier,
                enable_combat_rating,
                enable_cosmetic_rating,
                robot_id,
                creator_id,
                creator_nick_name,
                name,
                description,
                cpu,
                buy_count,
                battle_count,
                featured,
                tier,
                combat_rating,
                cosmetic_rating,
                _csv):
    f = open("./bots.csv", "r")
    reader = csv.reader(f)
    rows = [row for row in reader]
    f.close()

    if enable_robot_id:
        result = [row for row in rows if robot_id in row[0]]
        rows = result
        result = []
    if enable_creator_id:
        result = [row for row in rows if creator_id in row[4]]
        rows = result
        result = []
    if enable_nick_name:
        result = [row for row in rows if creator_nick_name in row[5]]
        rows = result
        result = []
    if enable_name:
        result = [row for row in rows if name in row[1]]
        rows = result
        result = []
    if enable_description:
        result = [row for row in rows if description in row[2]]
        rows = result
        result = []
    if enable_cpu:
        try:
            int(cpu)
            result = [row for row in rows if int(row[8]) == int(cpu)]
        except:
            result = [row for row in rows if (">" in cpu and "=" in cpu and int(row[8]) >= int(cpu[2:])) or 
                                            ("<" in cpu and "=" in cpu and int(row[8]) <= int(cpu[2:])) or
                                            (">" in cpu and int(row[8]) > int(cpu[1:])) or 
                                            ("<" in cpu and int(row[8]) < int(cpu[1:]))]
        rows = result
        result = []
    if enable_buy_count:
        try:
            int(buy_count)
            result = [row for row in rows if int(row[11]) == int(buy_count)]
        except:
            result = [row for row in rows if (">" in buy_count and "=" in buy_count and int(row[11]) >= int(buy_count[2:])) or
                                            ("<" in buy_count and "=" in buy_count and int(row[11]) <= int(buy_count[2:])) or
                                            ("<" in buy_count and int(row[11]) < int(buy_count[1:])) or 
                                            (">" in buy_count and int(row[11]) > int(buy_count[1:]))]
        rows = result
        result = []
    if enable_battlle_count:
        try:
            int(battle_count)
            result = [row for row in rows if int(row[10]) == int(battle_count)]
            
        except:
            result = [row for row in rows if (">" in battle_count and "=" in battle_count and int(row[10]) >= int(battle_count[2:])) or 
                                          ("<" in battle_count and "=" in battle_count and int(row[10]) <= int(battle_count[2:])) or 
                                          ("<" in battle_count and int(row[10]) < int(battle_count[1:])) or 
                                          (">" in battle_count and int(row[10]) > int(battle_count[1:]))]
        
        rows = result
        result = []
    if enable_featured:
        result = [row for row in rows if (featured == 1 and row[14] == "True") or (featured == 0 and row[14] == "False")]
        rows = result
        result = []   
    if enable_tier:
        result = [row for row in rows if (tier == 1 and int(row[9]) <= 1000) or 
                                        (tier == 2 and int(row[9]) <= 6434) or 
                                        (tier == 3 and int(row[9]) <= 79999) or 
                                        (tier == 4 and int(row[9]) <= 1299999) or 
                                        (tier == 5 and int(row[9]) >= 1300000) or 
                                        (tier == 6 and int(row[8]) >= 2001)]
        rows = result
        result = []
    if enable_combat_rating:
        result = [row for row in rows if (combat_rating == 1 and int(row[12]) <= 1.4) or 
                                        (combat_rating == 2 and int(row[12]) <= 2.4) or 
                                        (combat_rating == 3 and int(row[12]) <= 3.4) or 
                                        (combat_rating == 4 and int(row[12]) <= 4.4) or
                                        (combat_rating == 5 and int(row[12]) >= 4.5)]
        rows = result
        result = []
    if enable_cosmetic_rating:
        result = [row for row in rows if enable_combat_rating and 
        ((cosmetic_rating == 1 and int(row[13]) <= 1.4) or 
        (cosmetic_rating == 2 and int(row[13]) <= 2.4) or 
        (cosmetic_rating == 3 and int(row[13]) <= 3.4) or 
        (cosmetic_rating == 4 and int(row[13]) <= 4.4) or 
        (cosmetic_rating == 5 and int(row[13]) >= 4.5))]
        rows = result   

    if _csv:
        output = ""
        for i in range(len(rows)):
            output += ','.join(rows[i]) + "\n"
        rows = output

    return rows

def search_bots2(result, only_parts):
    embeds = []

    data_name = []
    data = []
    f = open("./essential_cubes.csv", "r")
    reader = csv.reader(f)

    for row in reader:
        if row[2].isdecimal() and not int(row[2]) in data:
            data_name.append(row[1])
            data.append(int(row[2]))

    f.close()
    
    for i in range(len(result)):

        if int(result[i][8]) > 2000:
            _tier = "TM"
        elif int(result[i][9]) <= 1000:
            _tier = 1
        elif int(result[i][9]) <= 6434:
            _tier = 2
        elif int(result[i][9]) <= 79999:
            _tier = 3
        elif int(result[i][9]) <= 1299999:
            _tier = 4
        else:
            _tier = 5
        
        if float(result[i][12]) <= 1.4:
            cbr = "⭐️"
        elif float(result[i][12]) <= 2.4:
            cbr = "⭐️⭐️"
        elif float(result[i][12]) <= 3.4:
            cbr = "⭐️⭐️⭐️"
        elif float(result[i][12]) <= 4.4:
            cbr = "⭐️⭐️⭐️⭐️"
        else:
            cbr = "⭐️⭐️⭐️⭐️⭐️"
        
        if float(result[i][13]) <= 1.4:
            csr = "⭐️"
        elif float(result[i][13]) <= 2.4:
            csr = "⭐️⭐️"
        elif float(result[i][13]) <= 3.4:
            csr = "⭐️⭐️⭐️"
        elif float(result[i][13]) <= 4.4:
            csr = "⭐️⭐️⭐️⭐️"
        else:
            csr = "⭐️⭐️⭐️⭐️⭐️"

        cubelist = ""
        cubedata = json.loads(result[i][15])
        keys = list(cubedata.keys())
        for k in range(len(data)):
            for j in range(len(cubedata)):

                if data[k] == int(keys[j]):
                    cubelist += data_name[k] + ": " + str(cubedata[keys[j]]) + "\n"

        if only_parts:
            embeds.append(discord.Embed(title="機体情報", description=cubelist))
            embeds[i].add_field(name="機体名",value=result[i][1],inline=False)
            embeds[i].add_field(name="作者",value=result[i][4] + " aka " + result[i][5],inline=False)
            embeds[i].set_footer(text="ID: " + result[i][0] + " • " + result[i][6])
            embeds[i].set_image(url=result[i][3])
        elif len(cubelist) > 384:
            embeds.append(discord.Embed(title="機体情報", description=""))
            embeds[i].add_field(name="機体名",value=result[i][1],inline=False)
            embeds[i].add_field(name="作者",value=result[i][4] + " aka " + result[i][5],inline=False)
            embeds[i].add_field(name="CPU",value=result[i][8],inline=False)
            embeds[i].add_field(name="ティア",value=str(_tier),inline=False)
            embeds[i].add_field(name="購入回数",value=result[i][10],inline=False)
            embeds[i].add_field(name="出撃回数",value=result[i][11],inline=False)
            embeds[i].add_field(name="戦闘評価",value=cbr,inline=False)
            embeds[i].add_field(name="外見評価",value=csr,inline=False)
            embeds[i].add_field(name="機体説明",value=result[i][2],inline=False)
            embeds[i].add_field(name="使用パーツ",value="使用パーツ過多のため省略",inline=False)
            embeds[i].add_field(name="出品期限",value=result[i][7],inline=False)
            embeds[i].set_footer(text="ID: " + result[i][0] + " • " + result[i][6])
            embeds[i].set_image(url=result[i][3])
        else:
            embeds.append(discord.Embed(title="機体情報"))
            embeds[i].add_field(name="機体名",value=result[i][1],inline=False)
            embeds[i].add_field(name="作者",value=result[i][4] + " aka " + result[i][5],inline=False)
            embeds[i].add_field(name="CPU",value=result[i][8],inline=False)
            embeds[i].add_field(name="ティア",value=str(_tier),inline=False)
            embeds[i].add_field(name="購入回数",value=result[i][10],inline=False)
            embeds[i].add_field(name="出撃回数",value=result[i][11],inline=False)
            embeds[i].add_field(name="戦闘評価",value=cbr,inline=False)
            embeds[i].add_field(name="外見評価",value=csr,inline=False)
            embeds[i].add_field(name="機体説明",value=result[i][2],inline=False)
            embeds[i].add_field(name="使用パーツ",value=cubelist,inline=False)
            embeds[i].add_field(name="出品期限",value=result[i][7],inline=False)
            embeds[i].set_footer(text="ID: " + result[i][0] + " • " + result[i][6])
            embeds[i].set_image(url=result[i][3])

    n = 10
    result = [embeds[idx:idx + n] for idx in range(0,len(embeds), n)]
    return result
            
def dl_bot(save_path, bot_info):
    with open(save_path, 'w') as f:
        json.dump(bot_info, f, indent=4)

    return discord.File(save_path, str(bot_info["id"]) + ".bot")

@tasks.loop(seconds=10)
async def loop():
    await client.wait_until_ready()

    # ロックを取得
    if loop_lock.locked():
        return
    
    #ロック開始
    async with loop_lock:
        ch = client.get_channel(1151360811705565204)

        embeds = await asyncio.get_event_loop().run_in_executor(None, crawler)

        if len(embeds) == 0:
            return

        for i in range(len(embeds)):
            data = {'embeds': [embed.to_dict() for embed in embeds[i]]}

            async with aiohttp.ClientSession() as session:
                async with session.post(WEBHOOK_URL, json=data) as response:
                    if response.status >= 400:
                        print(f'Failed to send embeds. Status code: {response.status}, Response: {await response.text()}')
                        
            try:
                await ch.send(embeds=embeds[i])
            except Exception as e:
                print(e)

@client.event
async def on_ready():
    print("起動完了")
    await client.change_presence(activity=discord.Game(name="Robocraft"))
    await tree.sync()#スラッシュコマンドを同期
    if not loop.is_running():
        await loop.start()

@tree.command(name="crf_bot_where",description="ANTI-NYA BOT")
@app_commands.describe(robot_id="機体ID")
@app_commands.describe(creator_id="2017年以前のアカウントなら初期ユーザー名、それ以降ならユーザーID")
@app_commands.describe(creator_nick_name="現在のユーザー名")
@app_commands.describe(name="機体名")
@app_commands.describe(description="機体説明")
@app_commands.describe(featured="FJのお気に入りだったもの")
@app_commands.describe(cpu="機体のCPU 例:>1750, <=1750 (オプション)")
@app_commands.describe(buy_count="購入回数 例:>1750, <=1750 (オプション)")
@app_commands.describe(battle_count="戦闘回数 例:>1750, <=1750 (オプション)")
@app_commands.describe(tier="ティア (オプション)")
@app_commands.describe(combat_rating="戦闘評価 (オプション)")
@app_commands.describe(cosmetic_rating="外観評価 (オプション)")
@app_commands.describe(csv="csv出力(only_partsが指定されている場合は無視されます)")
@app_commands.describe(only_parts="パーツのみ")
@app_commands.choices(                                                      
                        featured=[discord.app_commands.Choice(name="True",value=1), 
                            discord.app_commands.Choice(name="False",value=0)],
                        tier=[discord.app_commands.Choice(name="T1",value=1), 
                            discord.app_commands.Choice(name="T2",value=2), 
                            discord.app_commands.Choice(name="T3",value=3),
                            discord.app_commands.Choice(name="T4",value=4), 
                            discord.app_commands.Choice(name="T5",value=5), 
                            discord.app_commands.Choice(name="TM",value=6)],
                        combat_rating=[discord.app_commands.Choice(name="⭐️",value=1), 
                            discord.app_commands.Choice(name="⭐️⭐️",value=2), 
                            discord.app_commands.Choice(name="⭐️⭐️⭐️",value=3), 
                            discord.app_commands.Choice(name="⭐️⭐️⭐️⭐️",value=4), 
                            discord.app_commands.Choice(name="⭐️⭐️⭐️⭐️⭐️",value=5)],
                        cosmetic_rating=[discord.app_commands.Choice(name="⭐️",value=1), 
                            discord.app_commands.Choice(name="⭐️⭐️",value=2), 
                            discord.app_commands.Choice(name="⭐️⭐️⭐️",value=3), 
                            discord.app_commands.Choice(name="⭐️⭐️⭐️⭐️",value=4), 
                            discord.app_commands.Choice(name="⭐️⭐️⭐️⭐️⭐️",value=5)])
async def test_command(interaction: discord.Interaction, robot_id:str="", creator_id:str="", creator_nick_name:str="", name:str="", description:str="", 
                       featured:int=-1, cpu:str="", buy_count:str="", battle_count:str="", tier:int=0, combat_rating:int=0, cosmetic_rating:int=0, 
                       csv:bool=False, only_parts:bool=False):

    if robot_id == "" and creator_id == "" and creator_nick_name == "" and name == "" and description == "" and featured == -1:
        if cpu != "" or buy_count != "" or battle_count != "" or tier != 0 or combat_rating !=0 or cosmetic_rating != 0 or csv or only_parts:
            await interaction.response.send_message("オプションのみでの検索はできません",ephemeral=True)
            return
        await interaction.response.send_message("一つ以上の引数を指定してください",ephemeral=True)
        return
    
    query = "SELECT * FROM bots WHERE "

    if robot_id != "":
        query += "id == " + robot_id
    if creator_id != "":
        query += "addedBy LIKE " + creator_id
    if creator_nick_name != "":
        query += "addedByDisplayName LIKE " + creator_nick_name
    if name != "":
        query += "name LIKE" + name
    if description != "":
        enable_description = 1
    if cpu != "":
        enable_cpu = 1
    if buy_count != "":
        enable_buy_count = 1
    if battle_count != "":
        enable_battlle_count = 1
    if featured != -1:
        enable_featured = 1
    if tier != 0:
        enable_tier = 1
    if combat_rating !=0:
        enable_combat_rating = 1
    if cosmetic_rating != 0:
        enable_cosmetic_rating = 1

    await interaction.response.defer()

    creator_id = creator_id
    creator_nick_name = creator_nick_name
    name = name
    description = description
        
    result = await asyncio.get_event_loop().run_in_executor(None, search_bots, 
                                                            enable_robot_id, 
                                                            enable_creator_id, 
                                                            enable_nick_name, 
                                                            enable_name, 
                                                            enable_description,
                                                            enable_cpu,
                                                            enable_buy_count,
                                                            enable_battlle_count,
                                                            enable_featured,
                                                            enable_tier,
                                                            enable_combat_rating,
                                                            enable_cosmetic_rating,
                                                            robot_id,
                                                            creator_id,
                                                            creator_nick_name,
                                                            name,
                                                            description,
                                                            cpu,
                                                            buy_count,
                                                            battle_count,
                                                            featured,
                                                            tier,
                                                            combat_rating,
                                                            cosmetic_rating,
                                                            csv)

    if len(result) <= 0:
        await interaction.followup.send("一致なし",ephemeral=True)
        return
        # await interaction.response.send_message("一致なし",ephemeral=True)
    
    if csv:
        await interaction.followup.send("`" + result + "`")
        return

    embeds = await asyncio.get_event_loop().run_in_executor(None, search_bots2, result, only_parts) 

    for i in range(len(embeds)):
        try:
            await interaction.followup.send(embeds=embeds[i])
        except Exception as e:
            print(e)

    return

@tree.command(name="is_buyable",description="機体が購入できるか確認")
@app_commands.describe(robot_id="機体ID")
async def tmp_command(interaction: discord.Interaction, robot_id:str=""):
    if robot_id == "":
        await interaction.response.send_message("機体IDを入力してください",ephemeral=True)
        return

    await interaction.response.defer()
    try:
        bot_info = await asyncio.get_event_loop().run_in_executor(None, factory.factory_bot, token, int(robot_id))
        if bot_info["buyable"] == False:
            await interaction.followup.send("機体名: " + bot_info["name"] + "\nこの機体は購入できません",ephemeral=True)
        else:
            await interaction.followup.send("機体名: " + bot_info["name"] + "\nこの機体は購入できます",ephemeral=True)
    except:
        await interaction.followup.send("そのIDの機体は存在しないか、IDが不正です",ephemeral=True)
    return

@tree.command(name="dl_bot",description="Botダウンロード")
@app_commands.describe(robot_id="機体ID")
async def tmp_command(interaction: discord.Interaction, robot_id:str=""):
    if robot_id == "":
        await interaction.response.send_message("機体IDを入力してください",ephemeral=True)
        return
    
    await interaction.response.defer()
    try:
        bot_info = await asyncio.get_event_loop().run_in_executor(None, factory.factory_bot, token, int(robot_id))
        save_path = "./" + str(bot_info["id"]) + ".bot"
        file = await asyncio.get_event_loop().run_in_executor(None, dl_bot, save_path, bot_info)

        await interaction.followup.send(file=file)
    except:
        await interaction.followup.send("そのIDの機体は存在しないか、IDが不正です",ephemeral=True)
    return

client.run(TOKEN)