class StationSettings:
  discord_token: str

  audio_source: str
  audio_channel: str

  def __init__(self, discord_token: str, audio_source: str, audio_channel: str):
    self.discord_token = discord_token
    self.audio_source = audio_source
    self.audio_channel = audio_channel
