import asyncio
import sqlite3
from siegeapi import Auth
from datetime import datetime

db_path = 'r6s_stats.db'  
usernames = ["Chromius.TAMU", "Glonk..", "Glonk.MB","ThiccPie.OU","Fallen.Rqnger","Strugg1er.","Timythiccums.MB","Boomerjet123","Coolrocket.TAMU","Galahad21588","Fallen.Cortex","Dlehard.","Nobetterdough","Blade2420","Rat_Squilla","Colonizer.BU","NotLappland","Koyeetchi","Kermitt.MB","Strix.BBy","PincheConcha","JoeHashish.TAMU","Polar...-","lostarkwhale","Asherzs","veists."]

import sqlite3
import asyncio
from siegeapi import Auth


##############[Player Stats]###################################
async def insert_player_data(db_path, player_data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

   
    insert_sql = '''
    INSERT INTO Player (Username, KD_Ratio, Ranked_Points, KOST, Ranked_Win_Percent, Games_Played)
    VALUES (?, ?, ?, ?, ?, ?)
    ON CONFLICT(Username) DO UPDATE SET
    KD_Ratio=excluded.KD_Ratio,
    Ranked_Points=excluded.Ranked_Points,
    KOST=excluded.KOST,
    Ranked_Win_Percent=excluded.Ranked_Win_Percent,
    Games_Played=excluded.Games_Played;
    '''
    print("INSTERTING " + player_data['username'])
    cursor.execute(insert_sql, (
        player_data['username'],
        player_data['kd_ratio'],
        player_data['ranked_points'],
        player_data['kost'],
        player_data['ranked_win_percent'],
        player_data['games_played']
    ))

    conn.commit()
    conn.close()



async def fetch_player_stats_for_sqlite(username, db_path, auth):
    auth = Auth("YourEmail", "YourPassword") #Ubisoft Email and Password
    
    try:
        player = await auth.get_player(name=username)
        today_date = datetime.now().strftime("%Y%m%d")
        current_season_start = "20240312"
        player.set_timespan_dates(current_season_start, today_date)
        await player.load_summaries()  
        await player.load_operators()
        await player.load_ranked_v2()  

        
        latest_season = max(player.ranked_summary.keys())
        latest_season_data = player.ranked_summary[latest_season]  

        
        total_matches = latest_season_data['Attacker'].matches_played + latest_season_data['Defender'].matches_played
        wins = player.ranked_profile.wins
        losses = player.ranked_profile.losses
        ranked_win_percent = (wins / (wins + losses)) if (wins + losses) > 0 else 0

        KDRATIO = player.operators.ranked.attacker[0].kill_death_ratio
        for X in player.operators.ranked.attacker:
            if X.kill_death_ratio != 0:
                KDRATIO = (X.kill_death_ratio + KDRATIO)/2
        for X in player.operators.ranked.defender:
            if X.kill_death_ratio != 0:
                    KDRATIO = (X.kill_death_ratio + KDRATIO)/2
        KDRATIO = KDRATIO/100

       
        

        #Extracting and transforming data for Player table
        player_data = {
            'username': player.name,
            'kd_ratio': KDRATIO,  
            'ranked_points': player.ranked_profile.rank_points,
            'kost': (latest_season_data['Attacker'].rounds_with_kost+latest_season_data['Defender'].rounds_with_kost)/2,  
            'ranked_win_percent': ranked_win_percent,
            'games_played': total_matches,
        }

        await insert_player_data(db_path, player_data)

    except Exception as e:
        print(f"Error fetching stats for {username}: {e}")
    finally:
        await auth.close()
   
############################[MAPS]###################################################################
async def insert_map_data(db_path, map_data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for map_name in map_data.keys():
        cursor.execute('''
            INSERT OR IGNORE INTO Map (MapName)
            VALUES (?);
        ''', (map_name,))
    conn.commit()
    conn.close()
    

########################[Operators]################################################################
async def insert_operator_data(db_path, operator_names):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for name in operator_names:
        cursor.execute('''
            INSERT OR IGNORE INTO Operator (OpName)
            VALUES (?);
        ''', (name,))
    conn.commit()
    conn.close()
########################[Player Maps]##############################################################
async def fetch_and_insert_map_stats(username, db_path, auth):
    auth = Auth("YourEmail", "YourPassword") #Ubisoft Email and Password
    player = await auth.get_player(name=username)
    today_date = datetime.now().strftime("%Y%m%d")
    current_season_start = "20240312" 
    player.set_timespan_dates(current_season_start, today_date)
    await player.load_maps()  

    map_stats = {}
    for map_stat in player.maps.ranked.all: 
        win_percent = (map_stat.matches_won / map_stat.matches_played) * 100 if map_stat.matches_played > 0 else 0
        map_stats[map_stat.map_name] = {
            'win_percent': win_percent,
            'matches_played': map_stat.matches_played
        }

   
    await insert_map_data(db_path, map_stats)  
    await insert_player_map_data(db_path, username, map_stats)  

async def insert_player_map_data(db_path, username, map_stats):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for map_name, data in map_stats.items():
        cursor.execute('''
            INSERT INTO PlayerMap (Username, MapName, Win_Percent, Matches_Played)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(Username, MapName) DO UPDATE SET
                Win_Percent=excluded.Win_Percent,
                Matches_Played=excluded.Matches_Played;
        ''', (username, map_name, data['win_percent'], data['matches_played']))
    conn.commit()
    conn.close()

########################[Player Operators]#########################################################
async def fetch_and_insert_operator_stats(username, db_path, auth):
    auth = Auth("YourEmail", "YourPassword") #Ubisoft Email and Password
    player = await auth.get_player(name=username)
    await player.load_operators()  

    operator_stats = {}
    for operator in player.operators.ranked.defender:  
        if operator.rounds_played > 0:  
            kd_ratio = (operator.kills / operator.death if operator.death > 0 else operator.kills)
            operator_stats[operator.name] = {
                'kd_ratio': kd_ratio,
                'role': "Unknown",  
                'kost': operator.rounds_with_kost / operator.rounds_played,
                'round_win_percent': (operator.rounds_won / operator.rounds_played) * 100,
                'rounds_played': operator.rounds_played
            }
    for operator in player.operators.ranked.attacker:  
        if operator.rounds_played > 0:  
            kd_ratio = (operator.kills / operator.death if operator.death > 0 else operator.kills)
            operator_stats[operator.name] = {
                'kd_ratio': kd_ratio,
                'role': "Unknown",  
                'kost': operator.rounds_with_kost / operator.rounds_played,
                'round_win_percent': (operator.rounds_won / operator.rounds_played) * 100,
                'rounds_played': operator.rounds_played
            }
    
    await insert_operator_data(db_path, operator_stats.keys())  
    await insert_player_operator_data(db_path, username, operator_stats)  


async def insert_player_operator_data(db_path, username, operator_stats):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    for op_name, data in operator_stats.items():
        cursor.execute('''
            INSERT INTO PlayerOperator (Username, OpName, KD_Ratio, Role, KOST, Round_Win_Percent, Rounds_Played)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(Username, OpName) DO UPDATE SET
                KD_Ratio=excluded.KD_Ratio,
                Role=excluded.Role,
                KOST=excluded.KOST,
                Round_Win_Percent=excluded.Round_Win_Percent,
                Rounds_Played=excluded.Rounds_Played;
        ''', (
            username,
            op_name,
            data['kd_ratio'],
            data['role'],
            data['kost'],
            data['round_win_percent'],
            data['rounds_played']
        ))
    conn.commit()
    conn.close()





async def main(usernames, db_path):
    auth = Auth("YourEmail", "YourPassword") #Ubisoft Email and Password
    for username in usernames:
        await fetch_player_stats_for_sqlite(username, db_path, auth)
        await fetch_and_insert_map_stats(username, db_path, auth)
        await fetch_and_insert_operator_stats(username, db_path, auth)
    await auth.close()

asyncio.run(main(usernames, 'r6s_stats.db'))



