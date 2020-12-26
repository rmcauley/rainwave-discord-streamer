#!/bin/env python3

import logging
import os

from discord import FFmpegPCMAudio as ffmpeg
from discord.ext import commands

import settings
from streamwave.streamwave import Streamwave

discord_logger = logging.getLogger("discord")
discord_logger.setLevel(settings.discord_log_level)

streamwave_logger = logging.getLogger("streamwave")
streamwave_logger.setLevel(settings.streamwave_log_level)

for station in settings.stations:
  print("starting")
  client = Streamwave(station)
  client.run(station.discord_token)
  print('rubbish')
