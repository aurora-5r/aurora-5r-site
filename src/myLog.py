
# import logging
# LOGLEVEL="DEBUG"

# class SrvLogFormat(logging.Formatter):

#     err_fmt  = "[E] %(message)s"
#     warn_fmt  = "[!] %(message)s"
#     info_fmt = "[I] %(module)s: %(lineno)d: %(message)s"
#     dbg_fmt = "[D- %(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"

#     def format(self, record):
#         original_style = self._style

#         if record.levelno == logging.DEBUG:
#             self._style = logging.PercentStyle(self.dbg_fmt)
#         if record.levelno == logging.INFO:
#             self._style = logging.PercentStyle(self.info_fmt)
#         if record.levelno == logging.WARNING:
#             self._style = logging.PercentStyle(self.warn_fmt)
#         if record.levelno == logging.ERROR:
#             self._style = logging.PercentStyle(self.err_fmt)

#         result = logging.Formatter.format(self, record)
#         self._style = original_style
#         return result

# numeric_level = getattr(logging, LOGLEVEL.upper(), None)
# if not isinstance(numeric_level, int):
#     raise ValueError('Invalid log level: %s' % loglevel)

# hdlr = logging.StreamHandler()
# hdlr.setFormatter(SrvLogFormat())
# logging.root.addHandler(hdlr)
# logging.root.setLevel(numeric_level)




import os
import json
import logging.config

def setup_logging(
    default_path='logging.json',
    default_level=logging.DEBUG,
    env_key='LOG_CFG'
):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)