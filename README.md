# Event Propagator Service

Event Propagator service that sends events to an HTTP API
- Periodically sends predefined JSON events to an HTTP endpoint
- Configurable interval, endpoint, and event source file
- Random event selection from a JSON array
- Asynchronous HTTP client with error handling and retries

## Requirements

- Poetry
- Python 3.11

## Setup

```
poetry install
```

## Make commands

```
# run service
make run-propagator

# run service at 0.05s frequency
make run-propagator-hf

# run tests
make test
```