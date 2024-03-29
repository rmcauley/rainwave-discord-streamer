import logging
from typing import List

from streamwave.settings_class import StationSettings

discord_log_level = logging.INFO
streamwave_log_level = logging.DEBUG

rainwave_api_url = "ws://core.rainwave.cc/api4/websocket/"
rainwave_user_id = 0
rainwave_api_key = "aaaaaaaaaaa"

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
