import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import sqlite3
import re

activators = ["ty", "thx", "thanks", "thank you"]
conn = sqlite3.connect("users.db")
cursor = conn.cursor()
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        rep INTEGER NOT NULL
    )
""")
conn.commit()

def give_honor(reciever_user):
    # Checks if user already in db
    check = cursor.execute("SELECT * FROM users WHERE user_id = ?", (reciever_user.id,)).fetchall()
    if check == []:
        current = 0
        cursor.execute("INSERT INTO users (user_id, rep) VALUES (?, ?)", (reciever_user.id, current + 1)) # If not, user's added
    else:   
        # If present, rep incremented
        user = cursor.execute("SELECT * FROM users WHERE user_id = ?", (reciever_user.id,)).fetchall()
        current = int(user[0][2])
        cursor.execute("UPDATE users SET rep = ? WHERE user_id = ?", (current + 1, reciever_user.id))
        conn.commit()
    return True

intents = discord.Intents.all()
client = commands.Bot(command_prefix=None, intents=intents)

@client.tree.command(name="check_honor", description="Find out the magnitude of honor you have recieved from people")
async def check_honor(interaction: discord.Interaction):
    check = cursor.execute("SELECT * FROM users WHERE user_id = ?", (interaction.user.id,)).fetchall()
    if check == []:
        current = 0
        await interaction.response.send_message("You have 0 Honor, gotta up your game! Start helping more people in the subject channels.")
    else:   
        # If present, rep incremented
        user = cursor.execute("SELECT * FROM users WHERE user_id = ?", (interaction.user.id,)).fetchall()
        current = int(user[0][2])
        await interaction.response.send_message(f"You have {current} Honor Points")
@client.event
async def on_message(message):
    mentioned_users = []
    for mentioned_user in message.mentions:
        mentioned_users.append(mentioned_user)
        message.content = re.sub(f"<@{mentioned_user.id}>", "", str(message.content))
        message.content = message.content.replace(" ", "")
    if message.content in activators:
        if message.reference: 
            # Finds which user somebody is trying to honor
            reciever_message_id = message.reference.message_id
            reciever_message = await message.channel.fetch_message(reciever_message_id)
            reciever_user = reciever_message.author
            if reciever_user.id == message.author.id:
                await message.channel.send("Lol you thought!")
            else:
                if give_honor(reciever_user) == True:
                    await message.channel.send(f"+1 Honor to {reciever_user}!")
        else:
            for mentioned_user in mentioned_users:
                if mentioned_user.id == message.author.id:
                    await message.channel.send("Lol you thought!")
                    continue
                if give_honor(mentioned_user) == True:
                    await message.channel.send(f"+1 Honor to {mentioned_user}!")
@client.event
async def on_ready():
    print("Ready!")
    await client.tree.sync()
client.run("token")
