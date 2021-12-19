import discord

def wrapper(func):
	def Default(author,guild,*args):
		e=discord.Embed(title=guild.name,colour=discord.Colour.purple())
		e.set_author(name=author.name,icon_url=author.avatar_url)
		return func.__get__(EMBEDS)(e,*args)#this return to normal function that we use //function .__get__(class instance)(function param)
	return Default


class EMBEDS():

	def __init__(self,message):
		self.message=message


	@wrapper
	@staticmethod
	def nowPlaying(e,track,artist,thumbnail,url):

		e.description='Now Playing'
		e.set_thumbnail(url=thumbnail)
		e.add_field(name='Track',value='[{}]({})'.format(track,url))
		
		if(artist is not None and artist!='Unknown' and artist!='None'):
			e.add_field(name='Artist', value=artist)

		return e

	@wrapper
	@staticmethod
	def userNotConnected(e):
		e.description='Please Join a voice Channel'
		return e


	@wrapper
	@staticmethod
	def botNotConnected(e):
		e.description='Bot Not Connected To any Voice Channel'
		return e


	@wrapper
	@staticmethod
	def differentChannel(e):
		e.description='Someone else is already listening to music in different channel!'
		return e


	@wrapper
	@staticmethod
	def resumed(e):
		e.description='Resumed'
		return e


	@wrapper
	@staticmethod
	def alreadyPlaying(e):
		e.description='Already Playing'
		return e


	@wrapper
	@staticmethod
	def stop(e):
		e.description='Bot Stopped'
		return e


	@wrapper
	@staticmethod
	def nothingPlaying(e):
		e.description='Nothing is Playing Currently.'
		return e


	@wrapper
	@staticmethod
	def paused(e):
		e.description='Paused'
		return e


	@wrapper
	@staticmethod
	def alreadyPaused(e):
		e.description='Bot Already Paused.'
		return e


	@wrapper
	@staticmethod
	def invalidName(e):
		e.description='Please Enter a Valid Song Name or URL.'
		return e


	@wrapper
	@staticmethod
	def invalidPlaylistLink(e):
		e.description='Please Enter A Valid Playlist URL.'
		return e


	@wrapper
	@staticmethod
	def addPlaylist(e,q,res):
		e.description=f"Added {res} Song{'' if res==1 else 's'} in Playlist {q}"
		return e


	@wrapper
	@staticmethod
	def YTError(e,reason):
		e.description=reason
		return e


	@wrapper
	@staticmethod
	def error(e):
		e.description='An Unknown Error Occurred.'
		return e


	@wrapper
	@staticmethod
	def YTunknownError(e):
		e.description='Some Unknown Error Occurred while Searching.'
		return e


	@wrapper
	@staticmethod
	def addedQueue(e,num):
		e.description='Added {} Song{} in Queue.'.format(num,'s' if num>1 else '')
		return e


	@wrapper
	@staticmethod
	def queueEmpty(e):
		e.description="Queue Empty!!!"
		return e


	@wrapper
	@staticmethod
	def shuffle(e,res):

		if(res):
			e.description='Shuffled the Queue.'
		else:
			e.description='Not Shuffling The Queue.'
		return e


	@wrapper
	@staticmethod
	def loop(e,res):

		if(res==1):
			e.description='Looping Current Song.'
		elif(res==2):
			e.description='Looping Current Queue.'
		else:
			e.description='Not Looping The Queue.'
		return e


	@wrapper
	@staticmethod
	def showPlaylists(e,res):
		
		if(res):
			s=''
			for i in res:
				s+=i[0]+'\n'
			e.add_field(name='Your Server Saved Playlists are:',value=s[:-1])
		else:
			e.description='Your Server has no Saved Playlists.'
		return e


	@wrapper
	@staticmethod
	def playlistNotFound(e):
		e.description='Playlist Not Found.'
		return e


	@wrapper
	@staticmethod
	def changedPlaylist(e,playlist):
		e.description=f'''Playlist changed to "{playlist}"'''
		return e
