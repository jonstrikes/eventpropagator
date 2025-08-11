import asyncio
import logging
import argparse

from pydantic import ValidationError

from eventpropagator.utils import setup_logging, load_config
from eventpropagator.propagator import EventPropagator

async def main():
    parser = argparse.ArgumentParser(description='Event Propagator Service')
    parser.add_argument('--interval', '-i', help='Interval in seconds')
    parser.add_argument('--endpoint', '-e', help='API endpoint URL')
    parser.add_argument('--events-file', '-f', help='Events JSON file path')
    parser.add_argument('--config', '-c', help='Configuration file path')
    parser.add_argument('--log-level', '-l', default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    setup_logging(args.log_level)
    
    try:
        config = load_config(
            config_path=args.config,
            interval_seconds=args.interval,
            api_endpoint=args.endpoint,
            events_file=args.events_file
        )
        
        propagator = EventPropagator(config)
        await propagator.run()
        
    except ValidationError as e:
        logging.error(f"Configuration validation error: {e}")
        return 1
    except Exception as e:
        logging.error(f"Service failed to start: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))