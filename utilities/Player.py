import discord
import asyncio
class Player:

    @staticmethod
    async def create_player(track: str,artist: str,thumbnail: str,YTurl: str,url: str,file: str='opus'):
        # the 'opus' library here is opus.dll on windows
        # or libopus.so on linux in the current directory
        # you should replace this with the location the
        # opus library is located in and with the proper filename.
        # note that on windows this DLL is automatically provided for you
        opts={
            "options": "-vn"
        }
        # if(not discord.opus.is_loaded()):
        #     discord.opus.load_opus(file)
        source=discord.FFmpegPCMAudio(url,**opts)
        source.artist=artist
        source.thumbnail=thumbnail
        source.YTurl=YTurl
        source.track=track
        return source