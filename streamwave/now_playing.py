import sys
import logging
import json
import websocket
from discord import Activity, ActivityType

MAX_LENGTH = 127
log = logging.getLogger("streamwave")


class NowPlaying:
    def __init__(self, sid, rainwave_user_id, rainwave_api_key):
        self.sid = sid
        self.rainwave_user_id = rainwave_user_id
        self.rainwave_api_key = rainwave_api_key

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
        return result[:MAX_LENGTH]

    # Function to be run in its own thread so that each bot can update its own status to the currently playing song, album, and artist
    async def start(self, client):
        def on_message(connected_ws, message):
            data = json.loads(message)
            if "sched_current" in data:
                formatted_song = self.format_song(data["sched_current"])
                log.debug(f"Updating song: {formatted_song}")
                now_play = Activity(
                    type = ActivityType.listening,
                    name=formatted_song,
                )
                if client.ws:
                    client.change_presence(activity=now_play)
            if "wserror" in data:
                log.error(f"Failed validation to Rainwave API. {message}")
                raise RuntimeError("Bad user ID/API key")
            if "wsok" in data:
                log.info("Connected to Rainwave API.")
                connected_ws.send(json.dumps({
                    "action": "check_sched_current_id",
                    "sched_id": 1,
                }))
            if "error" in data:
                log.error(message)

        def on_open(connected_ws):
            log.debug("Authorizing on Rainwave API")
            connected_ws.send(json.dumps({
                "action": "auth",
                "user_id": self.rainwave_user_id,
                "key": self.rainwave_api_key,
            }))

        try:
            log.debug("Connecting to Rainwave API")
            ws = websocket.WebSocketApp(
                url=f"ws://core.rainwave.cc/api4/websocket/{self.sid}",
                on_open=on_open,
                on_message=on_message,
            )
            return ws.run_forever()

        except:
            log.exception("Error connecting", exc_info=sys.exc_info())
            raise
