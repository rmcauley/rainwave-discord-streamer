import asyncio
import json
import websocket
import ssl
from time import time
from discord import Activity, ActivityType
from urllib import request


class NowPlaying:
    def __init__(self, sid):
        self.sid = sid

    def format_song(self, rw_event):
        result = ""
        if rw_event["type"] == "OneUp":
            result += "\U0001F31F PH: " + rw_event["name"] + " \U0001F3B5 "
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
        apiKey = "bcNWNSiG80"
        uid = "37003"
        auth = '{ "action": "auth", "user_id": ' + uid + ', "key": ' + apiKey + '}'
        sid = str(self.sid)
        uri = "wss://rainwave.cc/api4/websocket/"
        
        def on_message(ws, message):
            data = json.decode(message)
            if "sched_current" in data:
                now_play = Activity(
                        type = ActivityType.listening,
                        name=self.format_song(data["sched_current"]),
                        )
                if client.ws:
                    await client.change_presence(activity=now_play)
            elif "wserror" in data:
                raise RuntimeError("Bad user ID/API key")
            elif "wsok" in data:
                ws.send({
                    "action": "check_sched_current_id",
                    "sched_id": 1,
                    })

        ws = websocket.WebSocketApp(uri, on_message=on_message)
        ws.run_forever(skip_utf8_validation=True)
