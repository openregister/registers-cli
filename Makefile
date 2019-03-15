test:
	pipenv run pytest
.PHONY: test

check:
	pipenv run mypy -m registers
.PHONY: check

security_check:
	pipenv run bandit -r registers
.PHONY: security_check

lint:
	pipenv run flake8
.PHONY: lint



