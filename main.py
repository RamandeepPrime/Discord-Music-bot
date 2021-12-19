from discord.ext import commands
import os
import json
from youtube.ytdl import YT_DL
from database.database import Database

bot = commands.Bot(command_prefix=commands.when_mentioned_or ('-'), description="This is a Helper Bot")

@bot.event
async def on_ready():
	print("Bot is started")

if __name__ == "__main__":
	with open("config.json") as f:
		bot.config=json.load(f)
		
	with open('youtube/ytdlconfig.json') as f:
		bot.ydl_opts=json.load(f)

	bot.messageID={}
	bot.yt=YT_DL(bot.config["yt_api"])
	bot.Database=Database()
	for extension in os.listdir('Commands'):
		if(extension.endswith('.py')):
			bot.load_extension(f'''Commands.{extension[:-3]}''')#setting up bot to commands_for _bot
	
	bot.run(bot.config['token'])



