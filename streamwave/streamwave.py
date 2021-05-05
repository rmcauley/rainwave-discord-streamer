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
from .settings_class import StationSettings


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

    # establish background task, join the channel, and play the music
    async def on_ready(self) -> None:
        channel = self.get_channel(self.settings.audio_channel)
        source = self.settings.audio_source
        vc = await channel.connect()
        # use from_probe to avoid re-encoding the stream on its way to discord
        self.audio_source = await discord.FFmpegOpusAudio.from_probe(source)
        vc.play(self.audio_source)
