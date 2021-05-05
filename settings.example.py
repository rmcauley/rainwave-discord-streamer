import logging
from typing import List

from settings_class import StationSettings

discord_log_level = logging.INFO
streamwave_log_level = logging.DEBUG

stations: List[StationSettings] = [
    StationSettings(
        discord_token="MY_NAME_IS_ALL",
        audio_source="http://relay.rainwave.cc/all.ogg",
        audio_channel=1234567890,
        sid=5,
    ),
    StationSettings(
        discord_token="MY_NAME_IS_GAME",
        audio_source="http://relay.rainwave.cc/game.ogg",
        audio_channel=987654321,
        sid=1,
    ),
]
