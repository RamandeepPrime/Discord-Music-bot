import asyncio
import json
import youtube_dl
import requests,logging
from pprint import pprint
class YT_DL:

	def __init__(self,api_key:str) -> None:
		self.api_key=api_key
		self.baseurl='https://www.googleapis.com/youtube/v3/playlistItems'
		self.playlist_name_url='https://www.googleapis.com/youtube/v3/playlists'
		self.total=0

	def checkForError(self,response: dict)-> str:
		if(response.get('error',None)):
			reason=response['error']['errors'][0]['reason']
			if(reason=='playlistNotFound'):
				return 'The Playlist is Either Private or The Given Playlist Link is invalid.'
			elif(reason=='watchLaterNotAccessible'):
				return 'WatchLaterPlaylists are not Accessible.'
			elif(reason=='watchHistoryNotAccessible'):
				return 'Watch History Playlists are not Acessible.'
			elif(reason=='playlistOperationUnsupported'):
				logging.getLogger('YtPlaylist.checkForError').error("The API Doesn't Support Either Enable it or Wait a few minutes if You enabled it Just yet.")
				return False
			else:
				return 'Some Unknown Error Occurred.'
		return True

	@staticmethod
	async def grab_video(self,ydl_opts:dict,video_link:str,loop=None)->map:
		
		
		ydl=youtube_dl.YoutubeDL(ydl_opts)
		if(not loop):loop=asyncio.get_event_loop()

		try:
			info =  await loop.run_in_executor(None,lambda: ydl.extract_info(video_link,download=False))

		except Exception as reason:
			return False

		# pprint(info['formats'])
		for i in info["formats"]:
			if 'acodec' in i and i['acodec'] == 'opus':
				info['src']=i['url']
				break
		
		
		return {'data':[info.get('track',info.get('title','Unknown')),
				info.get('artist'),
				info.get('thumbnail'),
				info.get('webpage_url')],
				'src':info['src']
			}

	
	def grab_video_data(self,playlistID: str)-> list:
		
		try:
			parameters={
				'part': 'snippet',
				'key': self.api_key,
				'playlistId': playlistID,
				'maxResults': 50
			}
			songs=[]
			nextPageToken=True
			while(nextPageToken):

				if(nextPageToken is not True):
					parameters['pageToken']=nextPageToken


				data=requests.get(self.baseurl,params=parameters).json()
				check=self.checkForError(response=data)

				if(check is not True):
					return check

				nextPageToken=data.get('nextPageToken',False)
				self.total=data['pageInfo']['totalResults']
				for song in data['items']:
					artist=song['snippet']['videoOwnerChannelTitle']
					if(artist.endswith('- Topic')):
						artist=artist[:-7]

						
					songs.append([song['snippet']['title'],
							artist,
							song['snippet']['thumbnails']['medium']['url'],
							'https://www.youtube.com/watch?v='+song['snippet']["resourceId"]["videoId"]])
	
			return songs

		except:

			logging.getLogger('YTPlaylists.getVideoData').error(exc_info=True)
			return False


	def playlist_name(self,playlistID:str):

		try:
			parameters={
					'part': 'snippet',
					'key': self.api_key,
					'id': playlistID,
				}

			return requests.get(self.playlist_name_url,params=parameters).json()["items"][0]["snippet"]["title"]
		# return requests.get(self.playlist_name_url,params=parameters).json()
		except:
			logging.error("error in playlist_name",exc_info=True)
			return "Unknown"

	def grab_songs(self,playlistID:str)->map:
		
		songs=self.grab_video_data(playlistID=playlistID)
		if not songs :
			return False
		
		return {
			"data":songs,
			"playlist_name":self.playlist_name(playlistID=playlistID),
			"results":self.total
		}

		

if __name__=="__main__":

	def halwa():
		with open('youtube/ytdlconfig.json') as f:
			ydl_opts=json.load(f)
		# monkey = asyncio.run( YT_DL.grab(ydl_opts,'https://www.youtube.com/watch?v=bi5PhlIQpwU'))
		# print(monkey)
		with open("config.json") as f:
			item=json.load(f)
		yt=YT_DL(item["yt_api"])
		# songs=asyncio.run(yt.grab_video_data(playlistID='RDCLAK5uy_ksEjgm3H_7zOJ_RHzRjN1wY-_FFcs7aAU'))
		
		# songs=asyncio.run(yt.playlist_name(playlistId='RDCLAK5uy_ksEjgm3H_7zOJ_RHzRjN1wY-_FFcs7aAU'))
		# songs=yt.grab_songs('PL9H4C1LWJf7SmBleg1V8HgNM2Wyn7whCA')
		songs=yt.grab_songs('PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj')
		# songs=asyncio.run(yt.grab_video(ydl_opts,video_link="hHUbLv4ThOo"))
		# songs=asyncio.run(yt.grab_video(ydl_opts,video_link="hHUbLv4ThOo"))
		pprint(songs)



			
	halwa()
