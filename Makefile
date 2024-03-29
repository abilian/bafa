.PHONY: all develop test lint clean doc format
.PHONY: clean clean-build clean-pyc clean-test coverage dist docs install lint lint/flake8

# The package name
PKG=bafa


all: test lint

#
# Setup
#
develop: install-deps activate-pre-commit configure-git

install-deps:
	@echo "--> Installing dependencies"
	pip install -U pip setuptools wheel
	poetry install

activate-pre-commit:
	@echo "--> Activating pre-commit hook"
	pre-commit install

configure-git:
	@echo "--> Configuring git"
	git config branch.autosetuprebase always


#
# testing & checking
#
test-all: test test-readme

test: ## run tests quickly with the default Python
	@echo "--> Running Python tests"
	pytest --ff -x -p no:randomly
	@echo ""

test-randomly:
	@echo "--> Running Python tests in random order"
	pytest
	@echo ""

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

	pytest
	@echo ""

test-with-coverage:
	@echo "--> Running Python tests"
	py.test --cov $(PKG)
	@echo ""

test-with-typeguard:
	@echo "--> Running Python tests with typeguard"
	pytest --typeguard-packages=${PKG}
	@echo ""

vagrant-tests:
	vagrant up
	vagrant ssh -c /vagrant/deploy/vagrant_test.sh


#
# Linting
#
.PHONY: lint/ruff
lint/ruff:
	ruff src tests/test*.py

.PHONY: lint
lint:
	ruff src tests/test*.py
	mypy --show-error-codes src
	flake8 src tests/test*.py
	# python -m pyanalyze --config-file pyproject.toml src
	lint-imports
	make hadolint
	vulture --min-confidence 80 src
	deptry . --extend-exclude .nox --extend-exclude .tox
	# TODO later
	# mypy --check-untyped-defs src

.PHONY: hadolint
hadolint:
	docker container run --rm -i \
		hadolint/hadolint hadolint --ignore DL3008 --ignore DL3059 -t style - < Dockerfile

.PHONY: audit
audit:
	pip-audit
	safety check

#
# Formatting
#
format: format-py format-js

format-py:
	docformatter -i -r src
	black src tests
	isort src tests

format-js:
	echo "TODO"


#
# Everything else
#
install:
	poetry install

doc: doc-html doc-pdf

doc-html:
	sphinx-build -W -b html docs/ docs/_build/html

doc-pdf:
	sphinx-build -W -b latex docs/ docs/_build/latex
	make -C docs/_build/latex all-pdf

clean:
	rm -f **/*.pyc
	find . -type d -empty -delete
	rm -rf *.egg-info *.egg .coverage .eggs .cache .mypy_cache .pyre \
		.pytest_cache .pytest .DS_Store  docs/_build docs/cache docs/tmp \
		dist build pip-wheel-metadata junit-*.xml htmlcov coverage.xml

tidy: clean
	rm -rf .tox .nox .dox .travis-solo
	rm -rf node_modules
	rm -rf instance

update-pot:
	# _n => ngettext, _l => lazy_gettext
	python setup.py extract_messages update_catalog compile_catalog

update-deps:
	pip install -U pip setuptools wheel
	poetry update
	poetry export -o requirements.txt

publish: clean
	git push --tags
	poetry build
	twine upload dist/*
