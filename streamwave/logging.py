import datetime
import logging


class RWFormatter(logging.Formatter):
    def format(self, record):
        msg = logging.Formatter.format(self, record)
        return "%s - %s - %s - %s" % (
            record.name.ljust(20),
            datetime.datetime.now().strftime("%m-%d %H:%M:%S"),
            record.levelname.ljust(8),
            msg,
        )
