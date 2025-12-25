from rolimons import Rolimons
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import math
import time
import asyncio

# Rolimons Trade Calculator
# Acts as a discord bot that uses preset commands to determine whether
# a trade is viable using Rolimon values.

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
required_role = "User"

trade_ads_g = {1: ["162066176", "19396550", "1172161", "10159610478"], 
               2: ["162066176", "9255011", "1172161", "10159610478"],
               3: ["162066176", "19396550", "1172161", "9255011"]}
trade_ads_r = {1: ["53039427", "141742418", "6552254"],
               2: ["293318274", "64560336", "130213380"],
               3: ["440739240", "63253701", "139577901"]}

current = 1 
class Client(commands.Bot):
    
    async def on_ready(self):
        print(f"{self.user.name} is activated")

        try:
            guild = discord.Object(id=1145805141291827272)
            synced = await self.tree.sync(guild=guild)
            print(f"Synced {len(synced)} commands to the the guild {guild.id}")

        except Exception as e:
            print(f"Error syncing commands: {e}")
    

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

client = Client(command_prefix="!", intents=intents)
GUILD_ID = discord.Object(id=1145805141291827272)

@client.tree.command(name="calculate", description="Determines whether a trade is good or not depending on the ids of the items given and received", guild=GUILD_ID)
async def Calculate(interaction: discord.Interaction, items_giving: str, items_receiving: str):
    if required_role not in [role.name for role in interaction.user.roles]:
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return
    rolimons = Rolimons()
    yourSideValue = 0
    theirSideValue = 0
    yourHighestDemand = 0
    theirHighestDemand = 0

    items_giving = items_giving.split(",")
    for id in items_giving:
        id = int(id)
        demandName, demandId = rolimons.getDemand(id)
        if demandId > yourHighestDemand:
            yourHighestDemand = demandId
        yourSideValue += rolimons.getValue(id)

    items_receiving = items_receiving.split(",")
    for id in items_receiving:
        id = int(id)
        demandName, demandId = rolimons.getDemand(id)
        if demandId > theirHighestDemand:
            theirHighestDemand = demandId
        theirSideValue += rolimons.getValue(id)

    isUpgrading = (len(items_giving) > len(items_receiving)) # upgrading is the act of giving multiple small items for a bigger item
    message = "Items you are giving:\n"
    for id in items_giving:
        message += rolimons.displayStats(id)
        message += "----------------------\n"
    message += f"Total Value: {yourSideValue}\n"
    
    message += "==========FOR==========\n"
    message += "Items you are receiving:\n"
    for id in items_receiving:
        message += rolimons.displayStats(id)
        message += "----------------------\n"
    message += f"Total Value: {theirSideValue}\n"
    message += "\n"
    if isUpgrading: # if we are upgrading then losing up to 5% is fine
        message += "You are upgrading\n"
        calculatedRate = 1 / (1 + (theirHighestDemand/100))
        
        if (yourSideValue/theirSideValue <= calculatedRate):
            message += "Adequate trade"
        else:
            message += "You are overpaying too much"
    else: # if we are downgrading then we need a gain that slightly decreases the more expensive the item is, but increases based off demand
        message += "You are downgrading\n"
        calculatedRate = (1/ (2*math.log(yourSideValue, 10))) * (1 + (yourHighestDemand/100))

        if (yourSideValue/theirSideValue >= calculatedRate):
            message += "Adequate trade"
        else:
            message += "You are getting lowballed"


    await interaction.response.send_message(message)

@client.tree.command(name="getinfo", description="Gets information about a specific item", guild=GUILD_ID)
async def GetInfo(interaction: discord.Interaction, item_id: int):
    if required_role not in [role.name for role in interaction.user.roles]:
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return
    rolimons = Rolimons()
    item_info = rolimons.displayStats(item_id)
    if not item_info:
        await interaction.response.send_message("Item not found.", ephemeral=True)
        return
    
    await interaction.response.send_message(item_info)

@client.tree.command(name="posttradead", description="Posts a trade advertisement in Rolimons", guild=GUILD_ID)
async def PostTradeAd(interaction: discord.Interaction):
    if required_role not in [role.name for role in interaction.user.roles]:
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return

    # respond immediately so Discord doesn't time out
    await interaction.response.send_message("Auto-post started. Posting will continue in the background.", ephemeral=True)

    rolimons = Rolimons()
    cookies = os.getenv("ROLI_COOKIES")
    if not cookies:
        # log and inform the caller
        logging.error("ROLI_COOKIES not set")
        return

    async def auto_post_loop(start_index: int = 1):
        idx = start_index
        channel = client.get_channel(interaction.channel_id)
        while True:
            try:
                items_giving = trade_ads_g[idx]
                items_receiving = trade_ads_r[idx]

                message = "Items you are giving:\n"
                yourSideValue = 0
                theirSideValue = 0

                for sid in items_giving:
                    id = int(sid)
                    yourSideValue += rolimons.getValue(id)
                    message += rolimons.displayStats(id)
                    message += "----------------------\n"

                message += f"Total Value: {yourSideValue}\n"
                message += "==========FOR==========\n"
                message += "Items you are receiving:\n"

                for sid in items_receiving:
                    id = int(sid)
                    theirSideValue += rolimons.getValue(id)
                    message += rolimons.displayStats(id)
                    message += "----------------------\n"

                message += f"Total Value: {theirSideValue}\n"
                response = rolimons.postTradeAd(cookies, [int(x) for x in items_giving], [int(x) for x in items_receiving], "upgrade", 1304608425)
                logging.info("postTradeAd response: %s", response)
                message += f"Response: \n{response}\n"

                if channel:
                    await channel.send(message)
                else:
                    # fallback to logging if channel can't be found
                    logging.info("Channel not found, message:\n%s", message)

            except Exception:
                logging.exception("Error in auto_post_loop")

            await asyncio.sleep(910)  # non-blocking sleep
            idx += 1
            if idx > len(trade_ads_g):
                idx = 1

    # start background task and return immediately
    client.loop.create_task(auto_post_loop(current))
    
    

client.run(token, log_handler=handler, log_level=logging.DEBUG)
