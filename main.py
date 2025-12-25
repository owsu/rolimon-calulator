from rolimons import Rolimons
import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import math

# Rolimons Trade Calculator
# Acts as a discord bot that uses preset commands to determine whether
# a trade is viable using Rolimon values.

load_dotenv()
token = os.getenv("DISCORD_TOKEN")
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
required_role = "User"

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
async def PostTradeAd(interaction: discord.Interaction, items_giving: str, items_receiving: str, request_tags: str, player_id: int):
    if required_role not in [role.name for role in interaction.user.roles]:
        await interaction.response.send_message("You do not have the required role to use this command.", ephemeral=True)
        return
    
    rolimons = Rolimons()
    message = "Items you are giving:\n"
    
    yourSideValue = 0
    theirSideValue = 0
    items_giving = [int(i) for i in items_giving.split(",")]
    items_receiving = [int(i) for i in items_receiving.split(",")]

    print(items_giving, items_receiving, request_tags, player_id)
    for id in items_giving:
        yourSideValue += rolimons.getValue(id)
        message += rolimons.displayStats(id)
        message += "----------------------\n"
    
    message += f"Total Value: {yourSideValue}\n"
    message += "==========FOR==========\n"
    message += "Items you are receiving:\n"
    
    for id in items_receiving:
        theirSideValue += rolimons.getValue(id)
        message += rolimons.displayStats(id)
        message += "----------------------\n"
    message += f"Total Value: {theirSideValue}\n"    
    response = rolimons.postTradeAd(os.getenv("ROLI_COOKIES"), items_giving, items_receiving, request_tags, player_id)
    print(response)
    message += f"Response: \n{response}\n"

    await interaction.response.send_message(message)

client.run(token, log_handler=handler, log_level=logging.DEBUG)
