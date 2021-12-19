# import requests
from pprint import pprint
from ytdl import YT_DL
import json
import asyncio
# baseurl='https://www.googleapis.com/youtube/v3/playlistItems'

# parameters={
#                 'part' : 'snippet',
#                 'key' : 'AIzaSyAT32bggiV8y1kVG9NQIXOaNdeWX97hThM',
#                 'playlistId' :'PL9H4C1LWJf7SmBleg1V8HgNM2Wyn7whCA',
#                 'maxResults' : 50
# 				#https://www.youtube.com/playlist?list=PL9H4C1LWJf7SmBleg1V8HgNM2Wyn7whCA
#             }


# data=requests.get(baseurl,params=parameters).json()
# pprint(data)

#part=contentDetails gives video id

#snippet give title,thumbnail,videoOwnerChannelTitle for author,video id
# args='https://www.youtube.com/watch?v=RgzLnmTaCAU&list=RDCLAK5uy_ksEjgm3H_7zOJ_RHzRjN1wY-_FFcs7aAU&start_radio=1&rv=bi5PhlIQpwU'
# for i in args.split('&'):
#     if(i[:5]=='list='):
#         args=i[5:]
# i=args.find('list=')

# print(args[i+5:args.find('&',i+5)])
from youtubesearchpython import VideosSearch
with open('youtube/ytdlconfig.json') as f:
	ydl_opts=json.load(f)
with open("config.json") as f:
	item=json.load(f)
yt=YT_DL(item["yt_api"])
videosSearch = VideosSearch('stay', limit = 1)
artist=videosSearch.result()
# artist=artist['result'][0]['channel']['name']
videoid=artist['result'][0]['id']
info=asyncio.run(yt.grab_video(ydl_opts,videoid))
pprint(info)

# songname=artist['result'][0]['title']
# thumbnail=artist['result'][0]['thumbnails']
# thumbnail=thumbnail[len(thumbnail)-1]['url']
# pprint(thumbnail)