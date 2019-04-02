test:
	pipenv run pytest --doctest-modules
.PHONY: test

coverage:
	pipenv run pytest --doctest-modules --cov-report=term --cov=registers
.PHONY: coverage

check:
	pipenv run mypy -p registers --warn-redundant-casts
.PHONY: check

security_check:
	pipenv run bandit -r registers
.PHONY: security_check

lint:
	pipenv run flake8
.PHONY: lint

# Pylint is more agressive than flake8. Good for development but not so much
# for CI.
pylint:
	pipenv run pylint registers
.PHONY: lint

# Build a single binary
dist:
	rm -rf dist build/registers
	pipenv run pyinstaller --clean -n registers --onefile cli.py
.PHONY: dist
