import asyncio
import json
from time import time
from discord import Activity, ActivityType
from urllib import request


class NowPlaying:
    def __init__(self, sid):
        self.sid = sid

    # Function to be run in its own thread so that each bot can update its own status to the currently playing song, album, and artist
    async def start(self, client):
        first = True
        sid = str(self.sid)
        while True:
            alist = ""
            song = ""
            # Current song data is the first song in the info API call
            with request.urlopen("http://rainwave.cc/api4/info?sid=" + sid) as url:
                data = json.loads(url.read().decode())
                artists = data["sched_current"]["songs"][0]["artists"]
                for a in artists:
                    alist += a["name"] + ", "
                alist = alist[: len(alist) - 2]
                song = data["sched_current"]["songs"][0]["title"]
                alb = data["sched_current"]["songs"][0]["albums"][0]["name"]
                # set status to the current song and artist
                # print(song)
                now_play = Activity(
                    type=ActivityType.listening,
                    name="\U0000266B "
                    + song
                    + "  \U0001F4D6 "
                    + alb
                    + "  \U0001F9B2 "
                    + alist,
                )
                if client.ws:
                    await client.change_presence(activity=now_play)
                # now we wait until the end of the song to check again
                end = data["sched_current"]["end"]
                start = data["sched_current"]["start_actual"]
                if first and time() > start:
                    sleeptime = end - time() + 5
                    first = False
                else:
                    sleeptime = end - start
                await asyncio.sleep(sleeptime)
