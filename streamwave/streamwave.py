import os
import discord
import asyncio
import threading
import logging
import urllib
import json
from time import time
from discord import Activity, ActivityType
from urllib import request 
from urllib.parse import urlparse
from discord.ext import commands
from dotenv import load_dotenv
from settings_class import StationSettings #contains discord channel IDs

#Function to be run in its own thread so that each bot can update its own status to the currently playing song, album, and artist
async def now_playing(self, client):
    first = True
    while True:
        alist = ""
        song = ""
        sid = str(self.settings.sid)
        #Current song data is the first song in the info API call
        with request.urlopen("http://rainwave.cc/api4/info?sid="+sid) as url:
            data = json.loads(url.read().decode())
            artists = data["sched_current"]["songs"][0]["artists"]
            for a in artists:
                alist += a["name"] + ", "
            alist = alist[:len(alist) - 2]
            song = data["sched_current"]["songs"][0]["title"]
            alb = data["sched_current"]["songs"][0]["albums"][0]["name"]
            #set status to the current song and artist
            #print(song)
            now_play = Activity(type=ActivityType.listening, name="\U0000266B "+song + "  \U0001F4D6 " + alb + "  \U0001F9B2 "+alist)
            await client.change_presence(self, activity=now_play)
            #now we wait until the end of the song to check again
            end = data["sched_current"]["end"]
            start = data["sched_current"]["start_actual"]
            if first and time() > start:
                sleeptime = end - time() + 5
                first = False
            else:
                sleeptime = end - start
            await asyncio.sleep(sleeptime)

class Streamwave(discord.Client):
    settings: StationSettings
    audio_source: discord.FFmpegOpusAudio

    def __init__(self, settings: StationSettings, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.settings = settings

    async def logout(self) -> None:
        for v in self.voice_clients:
            v.stop()
            await v.disconnect()
        await super().logout()

    def loop_in_thread(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(now_playing(self, discord.Client))

    #establish background task, join the channel, and play the music
    async def on_ready(self) -> None:
        loop = asyncio.get_event_loop()
        t = threading.Thread(target=self.loop_in_thread, args=(loop,))
        t.start()
        channel = self.get_channel(self.settings.audio_channel)
        source = self.settings.audio_source
        vc = await channel.connect()
        #use from_probe to avoid re-encoding the stream on its way to discord
        self.audio_source = await discord.FFmpegOpusAudio.from_probe(source)
        vc.play(self.audio_source)

