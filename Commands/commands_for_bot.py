from discord.ext import commands
from utilities.embeds import EMBEDS
# from youtube.ytdl import YT_DL
import discord
import logging
from utilities.Player import Player
from youtubesearchpython import VideosSearch
from pprint import pprint
#taking bot that load in main.py
class COMMANDS(commands.Cog):
	
	def __init__(self,bot):
		self.bot=bot

	@commands.command()
	async def ping(self,ctx):
		await ctx.send("pong")

	# @commands.command()
	# async def hi(self,ctx):
	# 	# embeds=EMBEDS.send_fucker()
	# 	await ctx.channel.send(embed=EMBEDS.send_fucker(ctx.author,ctx.guild))

	@commands.command()
	@commands.guild_only()
	async def play(self,ctx,*args):
		
		try:

			if(ctx.author.bot):return
			if(ctx.voice_client is None):
				return

			if(len(args)==0):
				if(ctx.voice_client.is_paused()):
					ctx.voice_client.resume()
					return

				else:
					song=self.bot.Database.get_songs(guildID=ctx.guild.id)
			
					if(song is None):
						await ctx.send(embed=EMBEDS.error(ctx.author,ctx.guild))
						return

					await self.start_playing(ctx,*song)
					return

				# else:
					
				# 	await ctx.send(embed=EMBEDS.invalidName(ctx.author,ctx.guild))
				# return

			args="".join(args)

			async with ctx.typing():

				i=args.find('list=')
				watch=args.find("watch")
				playlist=args.find('youtube.com/playlist?list=') #checking if its playlist or not
				# print('playlist',playlist)
				# print('i',i)
				total=0

				if(playlist>0 and i>0):

					total=await self.for_playlist(ctx,args,i)

				elif(watch>0):#if not playlist simple a song
					
					await self.for_song_links(ctx,args)
					total+=1

				# for name of songs
				else:
					
					await self.for_normal_songs(ctx,args)
					total+=1
			
			await ctx.send(embed=EMBEDS.addedQueue(ctx.author,ctx.guild,total))

			if(ctx.voice_client.is_playing()):
				return

			
			song=self.bot.Database.get_songs(guildID=ctx.guild.id)
			
			if(song is None):
				await ctx.send(embed=EMBEDS.error(ctx.author,ctx.guild))
				return

			await self.start_playing(ctx,*song)

		except Exception as e:
			logging.error("error in play",exc_info=True)


	async def for_playlist(self,ctx,args,i,add=0):

		try:
			
			# args=args[i+5:args.find('&',i+5)]#taking playlist id
			radio=args.find('&',i+5)
			if(radio>0):
				args=args[i+5:radio]#taking playlist id
			else :args=args[i+5:]
			
			
			info=self.bot.yt.grab_songs(playlistID=args)#data of playlist

			# pprint(info)
			# return
			if(info is False):
				await ctx.send(EMBEDS.YTunknownError(ctx.author,ctx.guild))
				return
			
			total=info['results']

			if(add):
				args=self.bot.Database.return_current_playlist(guildID=ctx.guild.id)
				if(args is None):args='unknown'
			
			#adding into the database
			
			# same thing if i else these 2 lines 
			self.bot.Database.add_into_guild(guildID=ctx.guild.id,playlistID=args)
			self.bot.Database.add_into_playlist(guildID=ctx.guild.id,playlistID=args,playlist_name=info['playlist_name'])

			# info gives {data :songs,playlistName,total songs in playlist}
			for i in info['data']:
						
				self.bot.Database.add_into_playlist_songs(song_details=i,playlistID=args,guildID=ctx.guild.id)

			return total

		except Exception as e:
			logging.error("error in for_playlist",exc_info=True)


	async def for_song_links(self,ctx,args):

		try:
			info=await self.bot.yt.grab_video(self=self.bot.yt,ydl_opts=self.bot.ydl_opts,video_link=args)

			if(info is False):
				await ctx.send(embed=EMBEDS.YTunknownError(ctx.author,ctx.guild))
				return

			playlistid=self.bot.Database.return_current_playlist(guildID=ctx.guild.id)

			if(playlistid is None):playlistid='unknown'

			self.bot.Database.add_into_playlist_songs(song_details=info['data'],playlistID=playlistid,guildID=ctx.guild.id)

		except Exception as e:
			logging.error("error in for_song_links",exc_info=True)

	
	async def for_normal_songs(self,ctx,args):

		try:
			
			videosSearch = VideosSearch(args, limit = 1)

			videoid=videosSearch.result()['result'][0]['id']
			info=await self.bot.yt.grab_video(self=self.bot.yt,ydl_opts=self.bot.ydl_opts,video_link=videoid)

			if(info is False):
				await ctx.send(embed=EMBEDS.YTunknownError(ctx.author,ctx.guild))
				return
				
			playlistid=self.bot.Database.return_current_playlist(guildID=ctx.guild.id)
	
			if(playlistid is None):playlistid='unknown'


			self.bot.Database.add_into_playlist_songs(song_details=info['data'],playlistID=playlistid,guildID=ctx.guild.id)

		except Exception as e:
			logging.error("error in for_normal_songs",exc_info=True)


	async def start_playing(self,ctx,*args):
		
		try:
			url=await self.bot.yt.grab_video(self=self.bot.yt,ydl_opts=self.bot.ydl_opts,video_link=args[3])

			if(url is False):
				await ctx.send(embed=EMBEDS.error(ctx.author,ctx.guild))
				return

			url=url['src']
				
			player=await Player.create_player(*args,url=url)
			ctx.voice_client.play(player,after=lambda x: self.bot.loop.create_task(self.done(ctx)))

			e=EMBEDS.nowPlaying(ctx.author,ctx.guild,player.track,player.artist,player.thumbnail, player.YTurl)
			self.bot.messageID[ctx.guild.id]=await ctx.send(embed=e)

		except Exception as e:
			logging.error("error in start_playing",exc_info=True)


	async def done(self,ctx):

		try:
			if ctx.voice_client is None:
				await ctx.send(embed=EMBEDS.botNotConnected(ctx.author,ctx.guild))
				return

			if (ctx.voice_client.is_playing()):
				ctx.voice_client.stop()

			message=self.bot.messageID.get(ctx.guild.id)

			if(message):
				await message.delete()

			song=self.bot.Database.get_songs(ctx.guild.id)

			if song is None:

				if(self.bot.messageID.get(ctx.guild.id)):
					self.bot.messageID.pop(ctx.guild.id)

				await ctx.send(embed=EMBEDS.queueEmpty(ctx.author,ctx.guild))
				await ctx.voice_client.disconnect()
				return

			await self.start_playing(ctx,*song)

		except Exception as e:
			logging.error("error in done")


	@commands.command()
	@commands.guild_only()
	async def add(self,ctx,args):

		try:
			# i have two options if i add normally or if voice client is None give it to play
			i=args.find('list=')
			watch=args.find("watch")
			playlist=(args.find('youtube.com/playlist?list=') and i)
			total=0
			if(ctx.author.bot):
				return

			args="".join(args)

			async with ctx.typing():
				if(playlist>0):

					total = await self.for_playlist(ctx,args,i,1)
					print(total)

				elif(watch>0):#if not playlist simple a song
					
					await self.for_song_links(ctx,args)
					total+=1

				# for name of songs
				else:
					
					await self.for_normal_songs(ctx,args)
					total+=1

			
			await ctx.send(embed=EMBEDS.addedQueue(ctx.author,ctx.guild,total))

			# if(ctx.voice_client is None):return

			# if(ctx.voice_client.is_playing()):
			# 	return

			
			# song=self.bot.Database.get_songs(guildID=ctx.guild.id)
			
			# if(song is None):

			# 	await ctx.send(embed=EMBEDS.error(ctx.author,ctx.guild))
			# 	return

			# await self.start_playing(ctx,*song)

			

		except Exception as e:
			logging.error("Error occurred add",exc_info=True)
			await ctx.send(embed=EMBEDS.error(ctx.author,ctx.guild))



	@commands.command()
	@commands.guild_only()
	async def skip(self,ctx):

		try:
			if(ctx.author.bot):
				return

			if(ctx.voice_client is None):

				await ctx.send(embed=EMBEDS.botNotConnected(ctx.author,ctx.guild))
				return

			await self.done(ctx)
			return

		except Exception as e:
			logging.error("error in skip",exc_info=True)


	@commands.command()
	@commands.guild_only()
	async def shuffle(self,ctx):

		try: 
			if(ctx.author.bot):
				return
			
			if(ctx.voice_client is None):

				await ctx.send(embed=EMBEDS.botNotConnected(ctx.author,ctx.guild))
				return
			
			res=self.bot.Database.set_shuffle(ctx.guild.id)
			
			if(res is None):

				await ctx.send(embed=EMBEDS.error(ctx.author,ctx.guild))
				return
			
			await ctx.send(embed=EMBEDS.shuffle(ctx.author,ctx.guild,res))
			return

		except Exception as e:
			logging.error("error in shuffle",exc_info=True)
	

	@commands.command()
	@commands.guild_only()
	async def loop(self,ctx):

		try:
			if(ctx.author.bot):
				return

			if(ctx.voice_client is None):

				await ctx.send(embed=EMBEDS.botNotConnected(ctx.author,ctx.guild))
				return

			res=self.bot.Database.set_loop(ctx.guild.id)

			if(res is None):
				await ctx.send(embed=EMBEDS.error(ctx.author,ctx.guild))
				return
			
			await ctx.send(embed=EMBEDS.loop(ctx.author,ctx.guild,res))
			return

		except Exception as e:
			logging.error("error in loop",exc_info=True)


	@commands.command()
	@commands.guild_only()
	async def pause(self,ctx):
		try:
			if(ctx.author.bot): return

			if(not self.is_connected(ctx)):
				return
			
			if(ctx.voice_client.is_paused()):
				await ctx.send(embed=EMBEDS.alreadyPaused(ctx.author,ctx.guild))
				return

			ctx.voice_client.pause()

			await ctx.send(embed=EMBEDS.paused(ctx.author,ctx.guild),delete_after=10)

		except Exception as e:
			logging.error("error in pause",exc_info=True)


	@commands.command(aliases=['np','nowplaying'])
	@commands.guild_only()
	async def now(self,ctx):
		try:
			if(ctx.author.bot):return

			if(ctx.voice_client is None):
			
				ctx.send(embed=EMBEDS.botNotConnected(ctx.author,ctx.guild))
				return
			
			if(not ctx.voice_client.is_playing()):
				await ctx.send(embed=EMBEDS.nothingPlaying(ctx.author,ctx.guild))
				return
			
			source=ctx.voice_client.source
			await ctx.send(embed=EMBEDS.nowPlaying(ctx.author,ctx.guild,source.track,source.artist,source.thumbnail, source.YTurl))

		except Exception as e:
			logging.error("error in now",exc_info=True)
	

	@commands.command()
	@commands.guild_only()
	async def stop(self,ctx):

		try:
			if(ctx.author.bot): return

			if(not await self.is_connected(ctx)):
				return

			if(ctx.voice_client.source is None):

				await ctx.send(embed=EMBEDS.nothingPlaying(ctx.author,ctx.guild))
				return

			ctx.voice_client.stop()

			playlistid=self.bot.Database.return_current_playlist(guildID=ctx.guild.id)
			self.bot.Database.remove_playlist(guildID=ctx.guild.id,playlistID=playlistid)

			await ctx.send(embed=EMBEDS.stop(ctx.author,ctx.guild),delete_after=10)

		except Exception as e:
			logging.error("error in stop",exc_info=True)


	@commands.command()
	@commands.guild_only()
	async def resume(self,ctx):
		try:
			if(ctx.author.bot): return
			
			if(not await self.is_connected(ctx)):
				return
			
			if(ctx.voice_client.is_playing()):
			
				await ctx.send(embed=EMBEDS.alreadyPlaying(ctx.author,ctx.guild))
				return
			
			ctx.voice_client.resume()
			await ctx.send(embed=EMBEDS.resumed(ctx.author,ctx.guild),delete_after=10)

		except Exception as e:
			logging.error("error in resume",exc_info=True)
	

	@commands.command()
	@commands.guild_only()
	async def move(self,ctx):

		try: 
			if(ctx.author.bot):return

			elif(ctx.author.voice is None):
			
				await ctx.send(embed=EMBEDS.userNotConnected(ctx.author,ctx.guild))
				return
			
			elif(ctx.voice_client is None):
				await ctx.author.voice.connect()
			
			elif(ctx.voice_client.channel==ctx.author.voice.channel):
				return
			
			else:
				await ctx.voice_client.move_to(ctx.author.voice.channel)

		except Exception as e:
			logging.error("error in move",exc_info=True)


	@commands.command(aliases=['change','cp'])
	@commands.guild_only()
	async def changeplaylist(self,ctx,*args):
		
		try:
			
			if(ctx.author.bot):
				return

			args="".join(args)
			
			data=self.bot.Database.set_playlist(args,ctx.guild.id)

			if(data is None):
				await ctx.send(embed=EMBEDS.error(ctx.author,ctx.guild))

			elif(data is False):
				await ctx.send(embed=EMBEDS.playlistNotFound(ctx.author,ctx.guild))
			
			else:
				await ctx.send(embed=EMBEDS.changedPlaylist(ctx.author,ctx.guild,data))
		
		except Exception as e:
			logging.error("error in change_playlist",exc_info=True)


	async def is_connected(self,ctx):

		try:

			if(ctx.author.voice is None):
				await ctx.send(embed=EMBEDS.userNotConnected(ctx.author,ctx.guild))
				return False
			
			elif(ctx.voice_client is None):
				await ctx.send(embed=EMBEDS.botNotConnected(ctx.author,ctx.guild))
				return False
			
			elif(ctx.author.voice.channel!=ctx.voice_client.channel):
				await ctx.send(embed=EMBEDS.differentChannel(ctx.author,ctx.guild))
				return False
			
			return True
		
		except Exception as e:
			logging.error('An Error Occurred in is_connected',exc_info=True)


	@commands.command()
	@commands.guild_only()
	@play.before_invoke
	async def join(self,ctx):

		try:
			if(ctx.voice_client is None):

				if(ctx.author.voice):
					await ctx.author.voice.channel.connect()

				else:
					await ctx.channel.send(embed=EMBEDS.userNotConnected(ctx.author,ctx.guild))
				return

			elif(ctx.voice_client.channel.id!=ctx.author.voice.channel.id):
					await ctx.voice_client.move_to(ctx.author.voice.channel)#moving bot to new voice channel that we joined

		except Exception as e:
			logging.error("error while joining",exc_info=True)


	@commands.command(aliases=['showplaylist','playlists','showplaylists'])
	@commands.guild_only()
	async def show_playlists(self,ctx):

		if(ctx.author.bot):return
		
		res=self.bot.Database.return_playlist(ctx.guild.id)
		
		await ctx.send(embed=EMBEDS.showPlaylists(ctx.author,ctx.guild,res))
		return

#setting bot fuction to commands
def setup(bot):
	bot.add_cog(COMMANDS(bot))

