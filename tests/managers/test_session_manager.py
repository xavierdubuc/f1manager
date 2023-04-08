import unittest
from unittest.mock import Mock, patch
from f1_22_telemetry.packets import PacketSessionData, WeatherForecastSample
from managers.abstract_manager import Change
from managers.session_manager import SessionManager
from models.enums.session_type import SessionType
from models.enums.temperature_change import TemperatureChange
from models.enums.track import Track
from models.enums.weather import Weather

from models.session import Session
from datetime import timedelta


class SessionManagerTest(unittest.TestCase):
    def setUp(self):
        super().setUp()

    @patch('managers.abstract_manager.AbstractManager.create')
    def test_create(self, patch_create):
        patch_create.return_value = Session(
            track=Track.spa,
            session_duration=3600,
            session_time_left=1000,
        )
        forecasts = (
            WeatherForecastSample(
                session_type=1,
                time_offset=5,
                weather=1,
                air_temperature=12,
                track_temperature=22,
                track_temperature_change=1,
                air_temperature_change=0,
                rain_percentage=46
            ),
            WeatherForecastSample(
                session_type=1,
                time_offset=10,
                weather=2,
                air_temperature=13,
                track_temperature=24,
                track_temperature_change=2,
                air_temperature_change=1,
                rain_percentage=32
        ))
        packet = PacketSessionData(
            num_weather_forecast_samples=2,
            weather_forecast_samples=(WeatherForecastSample * 56)(*forecasts)
        )

        session = SessionManager.create(packet)
        patch_create.assert_called_once_with(packet)
        self.assertEqual(session.session_time_elapsed, timedelta(seconds=2600))
        self.assertEqual(session.track, Track.spa)
        self.assertEqual(len(session.weather_forecast), 2)
        self.assertEqual(session.weather_forecast[0].session_type, SessionType.fp1)
        self.assertEqual(session.weather_forecast[0].time_offset, 5)
        self.assertEqual(session.weather_forecast[0].weather, Weather.light_cloud)
        self.assertEqual(session.weather_forecast[0].air_temperature, 12)
        self.assertEqual(session.weather_forecast[0].air_temperature_change, TemperatureChange.up)
        self.assertEqual(session.weather_forecast[0].track_temperature, 22)
        self.assertEqual(session.weather_forecast[0].rain_percentage, 46)
        self.assertEqual(session.weather_forecast[0].track_temperature_change, TemperatureChange.down)
        self.assertEqual(session.weather_forecast[1].session_type, SessionType.fp1)
        self.assertEqual(session.weather_forecast[1].time_offset, 10)
        self.assertEqual(session.weather_forecast[1].weather, Weather.overcast)
        self.assertEqual(session.weather_forecast[1].air_temperature, 13)
        self.assertEqual(session.weather_forecast[1].air_temperature_change, TemperatureChange.down)
        self.assertEqual(session.weather_forecast[1].track_temperature, 24)
        self.assertEqual(session.weather_forecast[1].rain_percentage, 32)
        self.assertEqual(session.weather_forecast[1].track_temperature_change, TemperatureChange.no_change)

    @patch('managers.abstract_manager.AbstractManager.update')
    def test_update(self, patch_update):
        patch_update.return_value= {}
        forecasts = (
            WeatherForecastSample(
                session_type=1,
                time_offset=5,
                weather=1,
                air_temperature=12,
                track_temperature=22,
                track_temperature_change=1,
                air_temperature_change=0,
                rain_percentage=46
            ),
            WeatherForecastSample(
                session_type=1,
                time_offset=10,
                weather=2,
                air_temperature=13,
                track_temperature=24,
                track_temperature_change=2,
                air_temperature_change=1,
                rain_percentage=32
        ))
        packet = PacketSessionData(
            session_duration=1200,
            session_time_left=200,
            num_weather_forecast_samples=2,
            weather_forecast_samples=(WeatherForecastSample * 56)(*forecasts)
        )
        session = SessionManager.create(packet)

        new_forecasts = (
            WeatherForecastSample(
                session_type=1,
                time_offset=5,
                weather=2,
                air_temperature=13,
                track_temperature=24,
                track_temperature_change=2,
                air_temperature_change=1,
                rain_percentage=32
            ),
            WeatherForecastSample(
                session_type=1,
                time_offset=10,
                weather=3,
                air_temperature=23,
                track_temperature=44,
                track_temperature_change=1,
                air_temperature_change=2,
                rain_percentage=42
        ))
        new_packet = PacketSessionData(
            num_weather_forecast_samples=2,
            weather_forecast_samples=(WeatherForecastSample * 56)(*new_forecasts)
        )
        changes = SessionManager.update(session, new_packet)
        self.assertEqual(len(changes), 1)
        self.assertIn('weather_forecast', changes)
        self.assertEqual(changes['weather_forecast'].actual, session.weather_forecast)
        self.assertEqual(len(session.weather_forecast), 2)
        self.assertEqual(session.weather_forecast[0].session_type, SessionType.fp1)
        self.assertEqual(session.weather_forecast[0].time_offset, 5)
        self.assertEqual(session.weather_forecast[0].weather, Weather.overcast)
        self.assertEqual(session.weather_forecast[0].air_temperature, 13)
        self.assertEqual(session.weather_forecast[0].air_temperature_change, TemperatureChange.down)
        self.assertEqual(session.weather_forecast[0].track_temperature, 24)
        self.assertEqual(session.weather_forecast[0].rain_percentage, 32)
        self.assertEqual(session.weather_forecast[0].track_temperature_change, TemperatureChange.no_change)
        self.assertEqual(session.weather_forecast[1].session_type, SessionType.fp1)
        self.assertEqual(session.weather_forecast[1].time_offset, 10)
        self.assertEqual(session.weather_forecast[1].weather, Weather.light_rain)
        self.assertEqual(session.weather_forecast[1].air_temperature, 23)
        self.assertEqual(session.weather_forecast[1].air_temperature_change, TemperatureChange.no_change)
        self.assertEqual(session.weather_forecast[1].track_temperature, 44)
        self.assertEqual(session.weather_forecast[1].rain_percentage, 42)
        self.assertEqual(session.weather_forecast[1].track_temperature_change, TemperatureChange.down)

        patch_update.return_value= {} # needed to avoid side effects
        nchanges = SessionManager.update(session, new_packet)
        self.assertDictEqual(nchanges, {})

        def side_effect(session, packet):
            session.session_time_left = 199
            return {}
        patch_update.side_effect = side_effect
        nchanges = SessionManager.update(session, new_packet)
        self.assertEqual(session.session_time_elapsed, timedelta(seconds=1001))
        self.assertDictEqual(nchanges, {
            'session_time_elapsed': Change(timedelta(seconds=1000), timedelta(seconds=1001))
        })