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

  async def streamwave_start(self, channel) -> None:
    log.debug(f"Streaming to {self.settings.audio_channel}")
    source = self.settings.audio_source
    vc = await channel.connect()
    # restream the Opus stream to Discord, avoiding re-encoding
    audio_source = await discord.FFmpegOpusAudio.from_probe(source)
    vc.play(audio_source)

  async def streamwave_stop(self, channel) -> None:
    for v in self.voice_clients:
      if v.channel.id == channel.id:
        log.debug(f"Stopping streaming to {self.settings.audio_channel}")
        v.stop()
        await v.disconnect()

  async def logout(self) -> None:
    for v in self.voice_clients:
      v.stop()
      await v.disconnect()
    await super().logout()

  async def on_ready(self) -> None:
    # check to see if anyone's listening after we've started
    channel = self.get_channel(self.settings.audio_channel)
    if len(channel.members) > 0:
      log.debug(f"Start-up check: Listeners waiting on {self.settings.audio_channel}")
      await self.streamwave_start(channel)
    else:
      log.debug(f"Start-up check: Nobody waiting on {self.settings.audio_channel}")

  async def on_voice_state_update(self, member, before, after) -> None:
    channel = after.channel or before.channel
    if not channel or channel.id != self.settings.audio_channel:
      return

    # will represent the list of channels currently connected to
    voicelist = [v.channel.id for v in self.voice_clients]

    # if we're the only ones left, disconnect
    if len(channel.members) == 1 and channel.members[0].id == self.user.id:
      await self.streamwave_stop(channel)
    # if we haven't connected yet, start
    elif len(channel.members) > 0 and channel.id not in voicelist:
      await self.streamwave_start(channel)
