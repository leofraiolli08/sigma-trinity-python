"""Bounded local diagnostics. Never logs saves, profiles, chat or gameplay inputs."""
import json
import logging
from logging.handlers import RotatingFileHandler
import platform
import sys
from pathlib import Path
from release_info import RELEASE_ID

LOG_PATH=Path(__file__).resolve().parent/'logs'/'multiplayer.log'
_logger=None

def event(room,stage,**details):
    global _logger
    try:
        if _logger is None:
            LOG_PATH.parent.mkdir(exist_ok=True)
            _logger=logging.getLogger('sigma.multiplayer');_logger.setLevel(logging.INFO);_logger.propagate=False
            handler=RotatingFileHandler(LOG_PATH,maxBytes=512*1024,backupCount=2,encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'));_logger.addHandler(handler)
        data={'release':RELEASE_ID,'room':room.trace_id,'role':'host' if room.is_host else 'client',
              'stage':stage,'platform':platform.system(),'python':sys.version.split()[0],**details}
        _logger.info(json.dumps(data,ensure_ascii=False,default=str))
    except (OSError,ValueError):pass  # Diagnostics cannot prevent gameplay.
