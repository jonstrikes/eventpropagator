import aiohttp
import json
import random
import logging
import asyncio
from pathlib import Path
from typing import List, Dict, Any

from eventpropagator.models import Config


class EventPropagator:
    def __init__(self, config: Config):
        self.config = config
        self.events: List[Dict[str, Any]] = []
        self.session: aiohttp.ClientSession = None
        self.logger = logging.getLogger(__name__)
        
    async def load_events(self) -> None:
        try:
            events_path = Path(self.config.events_file)
            if not events_path.exists():
                raise FileNotFoundError(f"Events file not found: {self.config.events_file}")
                
            with open(events_path, 'r', encoding='utf-8') as f:
                self.events = json.load(f)
                
            self.logger.info(f"Loaded {len(self.events)} events from {self.config.events_file}")
            
        except (json.JSONDecodeError, FileNotFoundError, ValueError) as e:
            self.logger.error(f"Failed to load events: {e}")
            raise
    
    async def send_event(self, event: Dict[str, Any]) -> None:
        try:
            async with self.session.post(
                self.config.api_endpoint,
                json=event,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                if response.status == 200:
                    self.logger.info(f"Successfully sent event: {event}")
                else:
                    self.logger.warning(
                        f"API responded with status {response.status} for event: {event}"
                    ) 

        except asyncio.TimeoutError:
            self.logger.error(f"Timeout sending event: {event}")
        except aiohttp.ClientError as e:
            self.logger.error(f"Client error sending event {event}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error sending event {event}: {e}")
    
    async def run(self) -> None:
        self.logger.info(f"Starting Event Propagator Service")
        self.logger.info(f"Interval: {self.config.interval_seconds} seconds")
        self.logger.info(f"API Endpoint: {self.config.api_endpoint}")
        self.logger.info(f"Events File: {self.config.events_file}")
        
        await self.load_events()
        
        self.session = aiohttp.ClientSession()
        
        try:
            while True:
                # Randomly select an event
                selected_event = random.choice(self.events)
                await self.send_event(selected_event)
                
                # Wait for the configured interval
                await asyncio.sleep(self.config.interval_seconds)

        except KeyboardInterrupt:
            self.logger.info("Service stopped by user")
        except Exception as e:
            self.logger.error(f"Service error: {e}")
            raise
        finally:
            if self.session:
                await self.session.close()