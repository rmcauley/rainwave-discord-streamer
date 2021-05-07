import asyncio
import json
from time import time
from discord import Activity, ActivityType
from urllib import request


class NowPlaying:
    def __init__(self, sid):
        self.sid = sid

    def format_song(self, rw_event):
        result = ""
        if rw_event["type"] == "OneUp":
            result += "\U0001F31F POWER HOUR \U0001F3B5 "
        elif rw_event["type"] == "PVPElection":
            result += "\U0001F94A PVP \U0001F3B5 "

        song = rw_event["songs"][0]
        result += song["albums"][0]["name"]
        result += " \U0001F4C2 " + song["title"]
        result += " \U0001F58C " + ", ".join(artist["name"] for artist in song["artists"])
        return result

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
                now_play = Activity(
                    type=ActivityType.listening,
                    name=self.format_song(data["sched_current"]),
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
