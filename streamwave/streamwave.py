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
    # use from_probe to avoid re-encoding the stream on its way to discord
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
    if len(channel.voice_states) > 0:
      log.debug(f"Start-up check: Listeners waiting on {self.settings.audio_channel}")
      await self.streamwave_start(channel)
    else:
      log.debug(f"Start-up check: Nobody waiting on {self.settings.audio_channel}")

  async def on_voice_state_update(self, member, before, after) -> None:
    channel = None

    # only look at channel if state has been changed for us
    if str(after) != str(before):
      # after.channel will be None if disconnecting, populated if switching or connecting
      if after.channel is not None and after.channel.id == self.settings.audio_channel:
        channel = after.channel
      # before.channel will be None if connecting for first time, populated if they are coming from a different channel
      elif before.channel is not None and before.channel.id == self.settings.audio_channel:
        channel = before.channel

    if not channel:
      return

    # Filter out ourselves from the member list, and anyone else's voice status that's from another channel
    listeners = [
      member_id
      for member_id, voice_state
      in channel.voice_states.items()
      if member_id != self.user.id
      and voice_state.channel
      and voice_state.channel.id == self.settings.audio_channel
    ]

    # if we're the only ones left, disconnect
    if len(listeners) == 0:
      await self.streamwave_stop(channel)
    # if we don't have this channel ID in our voice client list, connect
    elif not next((v.channel.id for v in self.voice_clients), None):
      await self.streamwave_start(channel)
