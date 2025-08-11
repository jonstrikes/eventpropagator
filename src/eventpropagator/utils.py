import yaml
import logging
from pathlib import Path

from eventpropagator.models import Config

def load_config(config_path: str = None, **kwargs) -> Config:
    config_data = {}
    
    if config_path and Path(config_path).exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
    
    config_data.update({k: v for k, v in kwargs.items() if v is not None})
    return Config(**config_data)


def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )