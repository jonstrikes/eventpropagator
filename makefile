install:
	poetry install

test:
	poetry run pytest tests/ -v

run-propagator:
	poetry run python src/eventpropagator/main.py -c config.yaml

run-propagator-hf:
	poetry run python src/eventpropagator/main.py -c config.yaml -i 0.05
