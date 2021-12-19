import sqlite3
import logging
#temporary
from pprint import pprint
class Database:

	def __init__(self):
		self.connection=sqlite3.connect("database/database.db")
		# self.connection=sqlite3.connect(":memory")
		

	def __del__(self):
		self.connection.close()

	
	def create_guild(self):

		try :
			
			self.connection.execute(f"""CREATE TABLE IF NOT EXISTS Guild(
				GuildID TEXT UNIQUE,
				Loop INTEGER,
				Shuffle INTEGER,
				Current_playlistID TEXT

			)""")

			self.connection.commit()

		except Exception as e:
			logging.error("while creating guild ",exc_info=True)


	def add_into_guild(self,guildID:str,playlistID:str):
		
		try:
			self.create_guild()
			if(self.guild_exists(guildID)):return #cheching if duplicate entry not entered
			self.connection.execute(f'''INSERT OR IGNORE INTO Guild
			VALUES(
				"{guildID}",0,0,"{playlistID}"
			)''')
			
			self.connection.commit()

		except Exception as e:
			logging.error("while adding into guild",exc_info=True)


	def create_playlist(self):

		try :
			self.connection.execute(f'''CREATE TABLE IF NOT EXISTS Playlist(
				
				PlaylistID TEXT,
				Playlist_name TEXT,
				GuildID TEXT,
				Position INTEGER
				
			)''')

			self.connection.commit()

		except Exception as e:
			logging.error("while creating playlist ",exc_info=True)
			

	def add_into_playlist(self,guildID:str,playlistID:str,playlist_name="unknown"):
		
		try:
			self.create_playlist()
			if(self.playlist_exists(guildID,playlistID)):return #cheching if duplicate entry not entered
			self.connection.execute(f'''INSERT INTO Playlist
			VALUES (
				"{playlistID}","{playlist_name}","{guildID}",{0}
			)''')

			self.connection.commit()

		except Exception as e:
			logging.error("while adding into playlist",exc_info=True)

	def create_playlist_songs(self,playlistID:str):

		try:
			
			self.connection.execute(f'''CREATE TABLE IF NOT EXISTS "{playlistID}"(
				Position INTEGER PRIMARY KEY AUTOINCREMENT,
				SongName TEXT,
				Artist TEXT,
				Thumbnail TEXT,
				URL TEXT
			)''')

			self.connection.commit()

		except Exception as e:
			logging.error("while making playlist_songs",exc_info=True)

	def add_into_playlist_songs(self,song_details:list,playlistID:str,guildID:str):
		
		try:

			self.create_playlist_songs(playlistID)
			#thinking....
			if(playlistID=='unknown'):
				self.add_into_playlist(guildID=guildID,playlistID=playlistID)
				self.add_into_guild(guildID=guildID,playlistID=playlistID)
			
			
			if(self.playlist_songs_exists(song_details,playlistID)):return
			self.connection.executemany(f'''INSERT INTO "{playlistID}"
				(SongName,Artist,Thumbnail,URL)
				VALUES (?,?,?,?)

			''',[song_details])

			self.connection.commit()

		except Exception as e:
			logging.error("while adding songs",exc_info=True)


	def guild_exists(self,guildID:str)->bool:
		
		try:
			return self.connection.execute(f'''SELECT GuildID,PlaylistID from Guild 
				WHERE GuildID="{guildID}"
			''').fetchone()
				

		except Exception as e:
			return False

	def playlist_exists(self,guildID:str,playlistID:str)->bool:

		try:

			return self.connection.execute(f'''SELECT * FROM Playlist 
				WHERE GuildID="{guildID}" and PlaylistID="{playlistID}"
			''').fetchone()

		except Exception as e:

			logging.error("while checking playlist",exc_info=True)

	def playlist_songs_exists(self,song_details:str,playlistID:str)->bool:

		try:
			
			return self.connection.execute(f'''SELECT * From "{playlistID}"
				WHERE SongName="{song_details[0]}" and Artist="{song_details[1]}"
			''').fetchone()
			

		except Exception as e:

			logging.error("playlist songs already exists")
			return None

	def set_loop(self,guildID:str):

		try:
			self.connection.execute(f'''UPDATE Guild SET Loop=(Loop+1)%2
				WHERE GuildID="{guildID}" 
			''')

			self.connection.commit()

			return self.connection.execute(f'''SELECT Loop FROM Guild 
				WHERE GuildID="{guildID}" 
			''').fetchone()[0]

		except Exception as e:
			 logging.error("while set loop",exc_info=True)


	def set_shuffle(self,guildID:str):

		try:
			self.connection.execute(f'''UPDATE Guild SET Shuffle=(Shuffle+1)%2
				WHERE GuildID="{guildID}" 
			''')

			self.connection.commit()

			return self.connection.execute(f'''SELECT Shuffle FROM Guild 
				WHERE GuildID="{guildID}" 
			''').fetchone()[0]

		except Exception as e:
			logging.error("while setting shuffle",exc_info=True)


	def get_songs(self,guildID:str)->list:
		
		try:
			
			loop,shuffle,playlistID=self.connection.execute(f'''SELECT Loop,Shuffle,Current_playlistID FROM Guild
				WHERE GuildID="{guildID}" 
			''').fetchone()
			
			

			total=self.connection.execute(f'''SELECT COUNT(*) FROM "{playlistID}"
			''').fetchone()[0]
			
			position=self.connection.execute(f'''SELECT Position FROM Playlist
				WHERE GuildID="{guildID}" and PlaylistID="{playlistID}"
			''').fetchone()[0]


			if(position==total):
				if(loop):position=0
				else: return None #we need to remove i think thats suggestion


			position+=1

			self.connection.execute(f'''UPDATE Playlist SET Position={position}
				WHERE GuildID="{guildID}" and PlaylistID="{playlistID}"
			''')

			self.connection.commit()

			if shuffle:
				return self.connection.execute(f'''SELECT SongName,Artist,Thumbnail,URL FROM "{playlistID}" 
					ORDER BY Random() Limit 1
				''').fetchone()
				
			return self.connection.execute(f'''SELECT SongName,Artist,Thumbnail,URL FROM "{playlistID}" 
				WHERE Position = {position}
			''').fetchone()
			


		except Exception as e:

			logging.error("while getting songs",exc_info=True)
			return None


	def remove_playlist(self,guildID:str,playlistID:str):

		try:
			
			# self.connection.execute(f'''DELETE FROM Guild 
			# 	WHERE GuildID="{guildID}" and PlaylistID ="{playlistID}"
			# ''')


			self.connection.execute(f'''DELETE FROM Playlist 
				WHERE GuildID="{guildID}" and PlaylistID ="{playlistID}"
			''')


			count=self.connection.execute(f'''SELECT COUNT(*) FROM Playlist
				WHERE PlaylistID="{playlistID}"
			''').fetchone()[0]

			if(count==0):

				self.connection.execute(f'''DROP TABLE "{playlistID}"
				''')

			current_playlist=self.connection.execute(f'''SELECT PlaylistID FROM Playlist
				WHERE GuildID='{guildID}'
			''').fetchone()[0]

			if(current_playlist):

				self.connection.execute(f'''UPDATE Guild SET 
					Current_playlistID="{current_playlist}"
					WHERE GuildID="{guildID}"
				''')

			else:

				self.connection.execute(f'''DELETE FROM Guild 
					WHERE GuildID="{guildID}" 
				''')


			self.connection.commit()

		except Exception as e:

			logging.error("while removing playlist",exc_info=True) 


	def return_playlist(self,guildID: int):

		try:
			return self.connection.execute(f"Select Playlist_name FROM Playlist WHERE GuildID='{guildID}'").fetchall()

		except Exception as e:
			logging.error("Error Occurred in ReturnPlaylists",exc_info=True)
			return False
	

	def set_playlist(self,playlist_name,guildID):

		try:

			current_playlist = self.connection.execute(f'''SELECT PlaylistID FROM Playlist
				WHERE Playlist_name LIKE '%{playlist_name}%'
			''').fetchone()[0]

			if(current_playlist is None):return None

			self.connection.execute(f'''UPDATE Guild SET 
				Current_playlistID="{current_playlist}" 
				WHERE GuildID="{guildID}"
			''')

			self.connection.commit()
			return current_playlist
			
		
		except Exception as e:
			logging.error("Error Occurred in set_playlist",exc_info=True)
			return False


	def return_current_playlist(self,guildID:str)->list:

		try:

			return self.connection.execute(f'''SELECT Current_playlistID FROM Guild
				WHERE GuildID="{guildID}"
			''').fetchone()[0]
		
		except Exception as e:

			logging.error("while showing current playlist",exc_info=True) 
			return None

	def show_playlist(self,guildID:str)->list:

		try:

			return self.connection.execute(f'''SELECT * FROM Playlist
				WHERE GuildID="{guildID}"
			''')
		
		except Exception as e:

			logging.error("while showing playlist",exc_info=True) 


	def show_all_playlists(self)->list:

		try:

			return self.connection.execute(f'''SELECT DISTINCT PlaylistID,Playlist_name FROM Playlist
			''')
		
		except Exception as e:

			logging.error("while showing all playlists",exc_info=True) 


#for debugging

if __name__=="__main__":

	a=Database()
	# a.add_into_guild("88","99")
	# print("Guild")
	# print(a.connection.execute(f'''SELECT * FROM Guild''').fetchall())
	# # fetchmany(it takes argument which amount of rows you need to print)
	
	# a.add_into_playlist("08899","98999")
	# a.add_into_playlist("88","99")
	# print("Playlist")
	# print(a.connection.execute(f'''SELECT * FROM Playlist''').fetchall())

	# #song details {songname, artist, thumbnail, Url} 
	# info={'data': ['Timber',
    #       'Pitbull feat. Ke$ha',
    #       'https://i.ytimg.com/vi_webp/hHUbLv4ThOo/maxresdefault.webp','hHUbLv4ThOo'],
 	# 	'src': 'https://r2---sn-5jucgv5qc5oq-qxae.googlevideo.com/videoplayback?expire=1637000156&ei=fE-SYfc2uf6O4w-b7bvIAg&ip=183.83.214.219&id=o-AD7oIsuRBkNJKF0BAqZDpSMjbegJFP0hXEJM1cbQuVvg&itag=249&source=youtube&requiressl=yes&mh=UR&mm=31%2C29&mn=sn-5jucgv5qc5oq-qxae%2Csn-qxa7sn7l&ms=au%2Crdu&mv=m&mvi=2&pl=22&gcr=in&initcwndbps=1306250&vprv=1&mime=audio%2Fwebm&ns=XbE0C6azR3TAtg4sqUAnOWgG&gir=yes&clen=1117936&dur=214.041&lmt=1583775504733729&mt=1636978138&fvip=2&keepalive=yes&fexp=24001373%2C24007246&beids=23886217&c=WEB&txp=5431432&n=GkF3k9hprFs0mUB6bY&sparams=expire%2Cei%2Cip%2Cid%2Citag%2Csource%2Crequiressl%2Cgcr%2Cvprv%2Cmime%2Cns%2Cgir%2Cclen%2Cdur%2Clmt&lsparams=mh%2Cmm%2Cmn%2Cms%2Cmv%2Cmvi%2Cpl%2Cinitcwndbps&lsig=AG3C_xAwRAIga0e_mPJzFVl2lxYNn-WGktUOg7ANmIprX_xoRy1H3K4CIBwxn0DlPPVgtOrD9RuR1WIBtllOxphocu77g_S0MST6&sig=AOq0QJ8wRQIhAJIHwhs6wwxt1VnSYQ0S6iRWNqlmr2j8yj2kAEFVHMZqAiB32bQDq9mgwOcJFHkubVpwvYw1bMdtT_eOAPr7wYRAMg=='}
	# a.add_into_playlist_songs(["tiktok","had","hghg","jkj"],"99")
	# a.add_into_playlist_songs(info['data'],"99",info['src'])
	# a.add_into_playlist_songs(["tikto","had","hghg","jkj"],"99")
	# print(a.connection.execute(f'''SELECT * FROM "99"''').fetchall())

	# # a.remove_playlist("88","99")
	# print(a.connection.execute(f'''SELECT * FROM Guild''').fetchall())
	# print(a.connection.execute(f'''SELECT * FROM Playlist ''').fetchall())
	# pprint(a.get_songs('88','99'))


	# a.add_into_playlist_songs(info['data'])
	#checking for unknown
	# a.add_into_playlist_songs(['timber','tilte','thumnail','url'],'unknown',guildID='99')

	# playlist= a.return_current_playlist("99")

	# a.add_into_playlist_songs(['tiktok','title','thumbnail','url'],playlist,guildID='99')

	# a.add_into_playlist('99','id','fuck')
	# a.set_loop('99')
	# a.set_shuffle('99')
	a.remove_playlist('99','unknown')
	# a.set_playlist('fuck','99')

	# a.connection.commit()

