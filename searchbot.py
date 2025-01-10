import csv
import json
import asyncio
# from PIL import Image
# import requests

from rcapi import auth, factory

import discord
from discord import app_commands
from discord.ext import tasks


TOKEN = ""

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
token = ""

stream_ch_id = 0

def get_bots():
    last = []
    f = open('bots.csv', 'r') #テキストを読み込む
    reader = csv.reader(f)
    rows = [row for row in reader]
    last = rows[-1]
    f.close() #テキスト読み込み終了

    count_bot = 1
    failed = 0
    while(1):
        try:
            if failed >= 5:
                count_bot -= failed
                break
            bot_info = factory.factory_bot(token, int(last[0]) + count_bot)
            save_path = "./bots/" + str(bot_info["id"]) + ".bot"
            print('Downloading %s to %s...' % (bot_info["name"], save_path))
            with open(save_path, 'w') as f:
                json.dump(bot_info, f, indent=4)
            failed = 0
            count_bot += 1
        except:
            failed += 1
            count_bot += 1
    
    count_bot -= 1

    if count_bot <= 0:
        return []
    elif count_bot >= 1:
        for j in range(int(last[0]) + 1, int(last[0]) + count_bot + 1):
            try:
                f = open("./bots/" + str(j) + ".bot", "r")
                fs = json.load(f)

                g = open("./bots.csv", "a")
                writer = csv.writer(g)
                writer.writerow([fs["id"], fs["name"], fs["description"], fs["thumbnail"], fs["addedBy"],\
                                fs["addedByDisplayName"], fs["addedDate"], fs["expiryDate"], fs["cpu"], fs["totalRobotRanking"],\
                                    fs["rentCount"], fs["buyCount"], fs["combatRating"], fs["cosmeticRating"],\
                                        fs["featured"], fs["cubeAmounts"]])

                f.close()
                g.close()
            except:
                pass

    result = []
    f = open("./bots.csv", "r")
    reader = csv.reader(f)
    for row in reader:

        for i in range(int(last[0]) + 1, int(last[0]) + count_bot + 1):
            if str(i) in row[0]:
                result.append(row)
    f.close()

    data_name = []
    data = []
    f = open("./essential_cubes.csv", "r")
    reader = csv.reader(f)

    for row in reader:
        if row[2].isdecimal() and not int(row[2]) in data:
            data_name.append(row[1])
            data.append(int(row[2]))

    f.close()
    embeds = []

    # megabot_flag = 0
    # for i in range(len(result)):
    #     if int(result[i][8]) > 2000:
    #         megabot_flag = 1

    for i in range(len(result)):
        # megabot_flag = 0
        # if int(result[i][8]) > 2000:
        #     megabot_flag = 1

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
        
        # if float(result[i][12]) <= 1.4:
        #     cbr = "⭐️"
        # elif float(result[i][12]) <= 2.4:
        #     cbr = "⭐️⭐️"
        # elif float(result[i][12]) <= 3.4:
        #     cbr = "⭐️⭐️⭐️"
        # elif float(result[i][12]) <= 4.4:
        #     cbr = "⭐️⭐️⭐️⭐️"
        # else:
        #     cbr = "⭐️⭐️⭐️⭐️⭐️"
        
        # if float(result[i][13]) <= 1.4:
        #     csr = "⭐️"
        # elif float(result[i][13]) <= 2.4:
        #     csr = "⭐️⭐️"
        # elif float(result[i][13]) <= 3.4:
        #     csr = "⭐️⭐️⭐️"
        # elif float(result[i][13]) <= 4.4:
        #     csr = "⭐️⭐️⭐️⭐️"
        # else:
        #     csr = "⭐️⭐️⭐️⭐️⭐️"

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

        if len(cubelist) > 768:
            embeds.append(discord.Embed(title="機体情報"))
            embeds[i].add_field(name="機体名",value=result[i][1],inline=False)
            embeds[i].add_field(name="作者",value=result[i][4] + " aka " + result[i][5],inline=False)
            embeds[i].add_field(name="CPU",value=result[i][8],inline=False)
            embeds[i].add_field(name="ティア",value=str(_tier),inline=False)
            # embeds[i].add_field(name="購入回数",value=result[i][10],inline=False)
            # embeds[i].add_field(name="出撃回数",value=result[i][11],inline=False)
            # embeds[i].add_field(name="戦闘評価",value=cbr,inline=False)
            # embeds[i].add_field(name="外見評価",value=csr,inline=False)
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
            # embeds[i].add_field(name="購入回数",value=result[i][10],inline=False)
            # embeds[i].add_field(name="出撃回数",value=result[i][11],inline=False)
            # embeds[i].add_field(name="戦闘評価",value=cbr,inline=False)
            # embeds[i].add_field(name="外見評価",value=csr,inline=False)
            embeds[i].add_field(name="機体説明",value=result[i][2],inline=False)
            embeds[i].add_field(name="使用パーツ",value=cubelist,inline=False)
            embeds[i].add_field(name="出品期限",value=result[i][7],inline=False)
            embeds[i].set_footer(text="ID: " + result[i][0] + " • " + result[i][6])
            embeds[i].set_image(url=result[i][3])
        
        # else:
        #     embeds.append("サムネ: " + result[i][3] + "\n" + \
        #         "機体ID: " + result[i][0] + "\n" + \
        #         "機体名: " + result[i][1] + "\n" + \
        #         "ユーザーID: " + result[i][4] + "\n" + \
        #         "ユーザー名: " + result[i][5] + "\n" + \
        #         "出品日: " +  result[i][6] + "\n" + \
        #         "出品期限: " +  result[i][7] + "\n" + \
        #         "CPU: " +  result[i][8] + "\n" + \
        #         "ティア: T" +  str(_tier) + "\n" + \
        #         # "購入回数: " +  result[i][11] + "\n" + \
        #         # "出撃回数: " +  result[i][10] + "\n" + \
        #         # "戦闘評価: " +  cbr + "\n" + \
        #         # "外見評価: " +  csr + "\n" + \
        #         "Featured: " +  result[i][14] + "\n" + \
        #         "機体説明: " + result[i][2] + "\n" + \
        #         "使用パーツ: \n" + cubelist)
    
    
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
            
@tasks.loop(seconds=180)
async def loop():
    await client.wait_until_ready()
    ch = client.get_channel(stream_ch_id)

    embeds = await asyncio.get_event_loop().run_in_executor(None, get_bots)

    if len(embeds) == 0:
        return

    for i in range(len(embeds)):
        await ch.send(embeds=embeds[i])

@client.event
async def on_ready():
    global token
    print("起動完了")
    credentials = await asyncio.get_event_loop().run_in_executor(None, auth.fj_login)
    token = credentials['Token']
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
    enable_robot_id = 0
    enable_creator_id = 0
    enable_nick_name = 0
    enable_name = 0
    enable_description = 0
    enable_cpu = 0
    enable_buy_count = 0
    enable_battlle_count = 0
    enable_featured = 0
    enable_tier = 0
    enable_combat_rating = 0
    enable_cosmetic_rating = 0

    if robot_id == "" and creator_id == "" and creator_nick_name == "" and name == "" and description == "" and featured == -1:
        if cpu != "" or buy_count != "" or battle_count != "" or tier != 0 or combat_rating !=0 or cosmetic_rating != 0 or csv or only_parts:
            await interaction.response.send_message("オプションのみでの検索はできません",ephemeral=True)
            return
        await interaction.response.send_message("一つ以上の引数を指定してください",ephemeral=True)
        return
    
    if robot_id != "":
        enable_robot_id = 1
    if creator_id != "":
        enable_creator_id = 1
    if creator_nick_name != "":
        enable_nick_name = 1
    if name != "":
        enable_name = 1
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
        enable_combat_rating = 1

    await interaction.response.defer()

    creator_id = creator_id.lower()
    creator_nick_name = creator_nick_name.lower()
    name = name.lower()
    description = description.lower()
        
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
        await interaction.followup.send(embeds=embeds[i])

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
        with open(save_path, 'w') as f:
                json.dump(bot_info, f, indent=4)

        file = discord.File(save_path, str(bot_info["id"]) + ".bot")
        await interaction.followup.send(file=file)
        
    except:
        await interaction.followup.send("そのIDの機体は存在しないか、IDが不正です",ephemeral=True)
    return

client.run(TOKEN)