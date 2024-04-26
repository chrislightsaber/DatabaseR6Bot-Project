import pandas as pd
import dataframe_image as dfi
import sqlite3
from discord.ext import commands
from discord import File
import discord

DB_PATH = 'r6s_stats.db'
PYTHON_SCRIPT_PATH = 'Rainbow Six Siege Tracker.py'

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all(), case_insensitive=True)

def execute_query(sql_query, params=None):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        if params:
            cursor.execute(sql_query, params)
        else:
            cursor.execute(sql_query)
        results = cursor.fetchall()
    return results

def create_dataframe_and_image(data, columns, filename):
    df = pd.DataFrame(data, columns=columns)
    styled_df = df.style.background_gradient()  
    dfi.export(styled_df, filename)
    return filename

@bot.command(name='refresh')
async def refresh(ctx):
    os.system(f'python {PYTHON_SCRIPT_PATH}')
    await ctx.send("Database has been updated.")

@bot.command(name='showtopbyrank')
async def show_top_by_rank(ctx):
    query = """
    SELECT Username, Ranked_Points FROM Player ORDER BY Ranked_Points DESC LIMIT 5
    """
    results = execute_query(query)
    response = "\n".join(f"{i+1}. {r[0]}, Points: {r[1]}" for i, r in enumerate(results))
    await ctx.send(f"Top 5 Players By Rank:\n{response}")

@bot.command(name='showtopbykd')
async def show_top_by_kd(ctx):
    query = """
    SELECT Username, KD_Ratio FROM Player ORDER BY KD_Ratio DESC LIMIT 5
    """
    results = execute_query(query)
    response = "\n".join(f"{i+1}. {r[0]}, K/D Ratio: {r[1]}" for i, r in enumerate(results))
    await ctx.send(f"Top 5 Players By K/D Ratio:\n{response}")

@bot.command(name='showtopbykost')
async def show_top_by_kost(ctx):
    query = """
    SELECT Username, KOST FROM Player ORDER BY KOST DESC LIMIT 5
    """
    results = execute_query(query)
    response = "\n".join(f"{i+1}. {r[0]}, KOST: {r[1]}" for i, r in enumerate(results))
    await ctx.send(f"Top 5 Players By KOST:\n{response}")

@bot.command(name='playerstats')
async def player_stats(ctx, username: str):
    query = """
    SELECT * FROM Player WHERE Username = ?
    """
    results = execute_query(query, (username,))
    if results:
        response = "\n".join(f"{key}: {value}" for key, value in zip(["Username", "KD Ratio", "Ranked Points", "KOST", "Ranked Win%", "Games Played"], results[0]))
        await ctx.send(f"Player Stats for {username}:\n{response}")
    else:
        await ctx.send(f"No stats found for {username}.")



@bot.command(name='playerops')
async def player_ops(ctx, username: str):
    query = "SELECT OpName, KD_Ratio, Role, KOST, Round_Win_Percent, Rounds_Played FROM PlayerOperator WHERE Username = ?"
    data = execute_query(query, (username,))
    if data:
        filename = f"{username}_ops_stats.png"
        columns = ["Operator", "K/D Ratio", "Role", "KOST", "Win%", "Rounds Played"]
        image_file = create_dataframe_and_image(data, columns, filename)
        await ctx.send(file=discord.File(image_file))
    else:
        await ctx.send(f"No operator data found for {username}.")

@bot.command(name='playermaps')
async def player_maps(ctx, username: str):
    query = "SELECT MapName, Win_Percent, Matches_Played FROM PlayerMap WHERE Username = ?"
    data = execute_query(query, (username,))
    if data:
        filename = f"{username}_maps_stats.png"
        columns = ["Map", "Win%", "Matches Played"]
        image_file = create_dataframe_and_image(data, columns, filename)
        await ctx.send(file=discord.File(image_file))
    else:
        await ctx.send(f"No map data found for {username}.")



@bot.command(name='R6help')
async def help_command(ctx):
    help_message = """
    Here are the available commands:
    `/refresh` - Update the database with the latest data.
    `/showtopbyrank` - Show top 5 players by ranked points.
    `/showtopbykd` - Show top 5 players by K/D ratio.
    `/showtopbykost` - Show top 5 players by KOST.
    `/playerstats <username>` - Show stats for a specific player.
    `/playermaps <username>` - Show map data for a specific player.
    `/playerops <username>` - Show operator data for a specific player.
    """
    await ctx.send(help_message)



bot.run('YourDiscordBotToken')
