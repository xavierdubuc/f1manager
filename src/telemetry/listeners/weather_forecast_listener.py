import logging
from datetime import datetime
from typing import Dict
from src.telemetry.event import Event

from src.telemetry.managers.abstract_manager import Change
from src.telemetry.models.session import Session
from .abstract_listener import AbstractListener

_logger = logging.getLogger(__name__)

DEFAULT_NOTIFICATION_DELAY = 4 * 60 # 5 minutes
DEFAULT_LOG_DELAY          = 1 * 60 # 1 minute

class WeatherForecastListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.SESSION_UPDATED
    ]

    def __init__(self, notification_delay=DEFAULT_NOTIFICATION_DELAY, log_delay=DEFAULT_LOG_DELAY):
        self.notification_delay = notification_delay
        self.log_delay = log_delay
        self.last_notified_at = None
        self.last_logged_at = None

    def _on_session_updated(self, session:Session, changes:Dict[str, Change]) -> str:
        if 'weather_forecast' not in changes:
            return
        now = datetime.now()
        log_delta = now - self.last_logged_at if self.last_logged_at else None
        if not log_delta or log_delta.seconds > self.log_delay:
            wfcasts = changes['weather_forecast'].actual
            str_wfcasts = []
            other_wfcasts = {}
            for wfcast in wfcasts:
                wf_values = str(wfcast)
                if wfcast.session_type == session.session_type:
                    str_wfcasts.append(wf_values)
                else:
                    other_wfcasts.setdefault(wfcast.session_type, [])
                    other_wfcasts[wfcast.session_type].append(wf_values)

            current_forecasts = '\n'.join(str_wfcasts)
            _logger.warning(current_forecasts)

            for sess_type, wfcasts in other_wfcasts.items():
                _logger.info('───────────────')
                _logger.info(sess_type)
                _logger.info('\n'.join(wfcasts))

            self.last_logged_at = now
        
            notification_delta = now - self.last_notified_at if self.last_notified_at else None
            if not notification_delta or notification_delta.seconds > self.log_delay:
                self.last_notified_at = now
                return current_forecasts