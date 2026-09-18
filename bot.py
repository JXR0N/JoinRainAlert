import discord
import asyncio
import sys
import os
from asyncio import sleep

from discord.ext import commands
from discord import app_commands

from dotenv import load_dotenv
from monitor import mainListener, logger 

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)
taskList = []

async def get_bot_token():
    try:
        load_dotenv()
        dcbottoken = os.getenv('dcbottoken')
        if dcbottoken is None:
            raise Exception
        logger.info(".env has been loaded successfully")
    except Exception:
        logger.error("Please Enter a valid Token!")
        sys.exit()
    return dcbottoken

async def toggleListener(state):
    for task in taskList:
        task.cancel()
    taskList.clear()
    
    if state:
        startListener = asyncio.create_task(start_listener())
        taskList.append(startListener)
        return startListener
    
async def start_listener():
    try: 
        while True:
            logger.info("Listener has been started")
            has_crashed = await mainListener(bot)

            if has_crashed:
                logger.info("Retry in 3 seconds")
                await sleep(3)


    except Exception as e:
        logger.error("Error while starting listener")
        

@bot.tree.command(name="stop_alert", description="stop alerts")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def stop_alert(interaction: discord.Interaction):
    await toggleListener(False)
    msg = "Bot has been stopped"
    logger.info(msg)
    await interaction.response.send_message(msg)

@bot.tree.command(name="start_alert", description="start alerts")
@app_commands.allowed_installs(guilds=True, users=True)
@app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
async def start_alert(interaction: discord.Interaction):
    msg = "Bot has been restarted"
    logger.info(msg)
    await interaction.response.send_message(msg)
    await toggleListener(True)
    


@bot.event
async def on_ready():
    logger.info(f'We have logged in as {bot.user}')
    sync = await bot.tree.sync()
    logger.info(f"Successfully synced {len(sync)} commands!")

    logger.info("Bot has been started")
    
    await toggleListener(True)
    

def main():
    token = asyncio.run(get_bot_token())
    bot.run(token)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.error("Error while executing script: ", e)
        sys.exit()
