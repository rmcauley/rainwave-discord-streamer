import asyncio
import logging
from urllib.parse import urlparse

import discord

from .settings_class import StationSettings

log = logging.getLogger("streamwave")


class Streamwave(discord.Client):
  settings: StationSettings

  def __init__(self, settings: StationSettings, *args, **kwargs) -> None:
    super().__init__(*args, **kwargs)
    self.settings = settings

  async def on_connect(self) -> None:
    log.debug("Connected")

  async def on_voice_state_update(self, member, before, after) -> None:
    # will represent the list of channels currently connected to
    voicelist = []
    for v in self.voice_clients:
      voicelist.append(v.channel.id)

    log.debug("Activity!")
    log.debug(str(voicelist))

    # someone joined or left a channel
    if str(after) != str(before):
      # someone joined an autojoin channel
      if after.channel is not None and after.channel.id == self.settings.audio_channel:
        log.debug(after.channel.id)
        log.debug(self.settings.audio_channel)
        # are we already in it? If not, join in.
        if after.channel.id not in voicelist:
          source = self.settings.audio_source
          channel = after.channel
          vc = await channel.connect()
          # restream the Opus stream to Discord, avoiding re-encoding
          audio_source = await discord.FFmpegOpusAudio.from_probe(source, codec="copy")
          vc.play(audio_source)

      # someone left an autojoin channel
      if before.channel is not None and before.channel.id == self.settings.audio_channel:
        # are we connected? If yes, check how many members are left.
        if before.channel.id in voicelist:
          channel = self.get_channel(before.channel.id)
          # if we're the only member left, it's time to leave.
          if len(channel.members) == 1:
            for v in self.voice_clients:
              if v.channel.id == channel.id:
                v.stop()
                await v.disconnect()
