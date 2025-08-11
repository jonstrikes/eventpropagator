import json
import pytest
from unittest.mock import patch, mock_open

from eventpropagator.models import Config
from eventpropagator.propagator import EventPropagator


class TestEventPropagator:
    @pytest.fixture
    def config(self):
        return Config(
            interval_seconds=1,
            api_endpoint="http://test.com/event",
            events_file="test_events.json"
        )
    
    @pytest.fixture
    def propagator(self, config):
        return EventPropagator(config)
    
    @pytest.fixture
    def sample_events(self):
        return [
            {"event_type": "message", "event_payload": "hello"},
            {"event_type":123, "event_payload":{}},
            {"foo": "bar"},
        ]
    
    @pytest.mark.asyncio
    async def test_load_events_success(self, propagator, sample_events):
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data=json.dumps(sample_events))):
                await propagator.load_events()

        assert propagator.events == sample_events
    
    @pytest.mark.asyncio
    async def test_load_events_file_not_found(self, propagator):
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(FileNotFoundError, match="Events file not found"):
                await propagator.load_events()
    
    @pytest.mark.asyncio
    async def test_load_events_invalid_json(self, propagator):
        with patch("pathlib.Path.exists", return_value=True):
            with patch("builtins.open", mock_open(read_data="invalid json")):
                with pytest.raises(json.JSONDecodeError):
                    await propagator.load_events()
