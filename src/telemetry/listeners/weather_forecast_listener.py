import logging
from datetime import datetime
from typing import Dict, List
from src.telemetry.event import Event

from src.telemetry.managers.abstract_manager import Change
from src.telemetry.models.session import Session
from src.telemetry.models.weather_forecast import WeatherForecast
from .abstract_listener import AbstractListener

_logger = logging.getLogger(__name__)

DEFAULT_NOTIFICATION_DELAY = 4 * 60 # 5 minutes
DEFAULT_LOG_DELAY          = 1 * 60 # 1 minute

class WeatherForecastListener(AbstractListener):
    SUBSCRIBED_EVENTS = [
        Event.SESSION_CREATED,
        Event.SESSION_UPDATED
    ]

    def __init__(self, notification_delay=DEFAULT_NOTIFICATION_DELAY, log_delay=DEFAULT_LOG_DELAY):
        self.notification_delay = notification_delay
        self.log_delay = log_delay
        self.last_notified_at = None
        self.last_logged_at = None

    def _on_session_created(self, current: Session, old: Session) -> str:
        now = datetime.now()
        wfcasts = current.weather_forecast
        current_forecasts = self._log_forecasts(wfcasts)
        self.last_logged_at = now
        self.last_notified_at = now
        return current_forecasts

    def _on_session_updated(self, session:Session, changes:Dict[str, Change]) -> str:
        if 'weather_forecast' not in changes:
            return
        now = datetime.now()
        log_delta = now - self.last_logged_at if self.last_logged_at else None
        if not log_delta or log_delta.seconds > self.log_delay:
            wfcasts = changes['weather_forecast'].actual
            current_forecasts = self._log_forecasts(wfcasts)
            self.last_logged_at = now
        
            notification_delta = now - self.last_notified_at if self.last_notified_at else None
            if not notification_delta or notification_delta.seconds > self.log_delay:
                self.last_notified_at = now
                return current_forecasts

    def _log_forecasts(self, session:Session, forecasts:List[WeatherForecast]) -> str:
        str_wfcasts = []
        other_wfcasts = {}
        for wfcast in forecasts:
            wf_values = str(wfcast)
            if wfcast.session_type == session.session_type:
                str_wfcasts.append(wf_values)
            else:
                other_wfcasts.setdefault(wfcast.session_type, [])
                other_wfcasts[wfcast.session_type].append(wf_values)

        # log current session forecast
        current_forecasts = '\n'.join(str_wfcasts)
        _logger.warning(current_forecasts)

        # log forecasts for other sessions
        for sess_type, wfcasts in other_wfcasts.items():
            _logger.info('───────────────')
            _logger.info(sess_type)
            _logger.info('\n'.join(wfcasts))

        return current_forecasts