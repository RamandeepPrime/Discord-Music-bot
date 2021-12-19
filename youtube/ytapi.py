import requests
from pprint import pprint
baseurl='https://www.googleapis.com/youtube/v3/playlistItems'

parameters={
                'part' : 'snippet',
                'key' : 'AIzaSyAT32bggiV8y1kVG9NQIXOaNdeWX97hThM',
                'playlistId' :'PL9H4C1LWJf7SmBleg1V8HgNM2Wyn7whCA',
                'maxResults' : 50
				#https://www.youtube.com/playlist?list=PL9H4C1LWJf7SmBleg1V8HgNM2Wyn7whCA
            }


data=requests.get(baseurl,params=parameters).json()
pprint(data)