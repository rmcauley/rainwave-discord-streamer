#!/usr/bin/env python

import asyncio
import logging
import typing

from discord import FFmpegPCMAudio as ffmpeg
from discord.ext import commands

import settings
from streamwave.logging import RWFormatter
from streamwave.streamwave import Streamwave
from streamwave.now_playing import NowPlaying

print_handler = logging.StreamHandler()
print_handler.setFormatter(RWFormatter())
print_handler.setLevel(logging.DEBUG)

discord_logger = logging.getLogger("discord")
discord_logger.setLevel(settings.discord_log_level)
discord_logger.addHandler(print_handler)

streamwave_logger = logging.getLogger("streamwave")
streamwave_logger.setLevel(settings.streamwave_log_level)
streamwave_logger.addHandler(print_handler)

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
clients: typing.List[Streamwave] = [
    Streamwave(station) for station in settings.stations
]
now_playings = []
try:
    for client in clients:
        now_playing = NowPlaying(
            client,
            client.settings.sid,
            settings.rainwave_api_url,
            settings.rainwave_user_id,
            settings.rainwave_api_key,
        )
        now_playings.append(now_playing)
        loop.create_task(client.start(client.settings.discord_token))
        loop.create_task(now_playing.start())
    loop.run_forever()
except KeyboardInterrupt:
    for client in clients:
        try:
            loop.run_until_complete(client.close())
        except:
            pass
    for now_playing in now_playings:
        try:
            loop.run_until_complete(now_playing.close())
        except:
            pass
finally:
    loop.close()
