import json
import pytest
import aiohttp
from yarl import URL
from aioresponses import aioresponses
from unittest.mock import patch, mock_open

from eventpropagator.models import Config
from eventpropagator.propagator import EventPropagator

@pytest.fixture(scope="module")
def config():
    return Config(
        interval_seconds=1,
        api_endpoint="http://test.com/event",
        events_file="test_events.json"
    )

@pytest.fixture(scope="module")
def propagator(config):
    return EventPropagator(config)

@pytest.fixture(scope="module")
def sample_events():
    return [
        {"event_type": "message", "event_payload": "hello"},
        {"event_type":123, "event_payload":{}},
        {"foo": "bar"},
    ]

class TestLoadEvents:
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


class TestSendEvents:
    @pytest.mark.asyncio
    async def test_send_event_success(self, propagator, sample_events):
        event = sample_events[0]
        
        with aioresponses() as m:
            m.post(propagator.config.api_endpoint, status=400)

            propagator.session = aiohttp.ClientSession()

            try:
                await propagator.send_event(event)
                
                assert len(m.requests) == 1
                request = m.requests[('POST', URL(propagator.config.api_endpoint))][0]
                assert request.kwargs['json'] == event
            finally:
                await propagator.session.close()

    @pytest.mark.asyncio
    async def test_send_event_400(self, propagator, sample_events, caplog):
        event = sample_events[0]
        
        with aioresponses() as m:
            m.post(propagator.config.api_endpoint, status=400)
            
            propagator.session = aiohttp.ClientSession()
            
            try:
                await propagator.send_event(event)
                print(caplog)
                assert "API responded with status 400" in caplog.text
            finally:
                await propagator.session.close()
