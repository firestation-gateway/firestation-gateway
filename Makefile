

VENV_NAME?=venv
VENV_ACTIVATE=. $(VENV_NAME)/bin/activate
PYTHON=${VENV_NAME}/bin/python3
PIP=${VENV_NAME}/bin/pip
COV=${VENV_NAME}/bin/coverage

ifeq ("$(origin V)", "command line")
  VERBOSE = $(V)
endif
ifndef VERBOSE
  VERBOSE = 0
endif

ifeq ($(VERBOSE),1)
  Q =
else
  Q = @
endif

all: venv

build:
	./build-wheel.sh

run: venv	

run-test: venv
	$(Q)$(PYTHON) -m pytest -vvs

run-lint: run-pylint run-ruff

run-pylint: venv
	@echo "Running pylint.."
	$(Q)$(VENV_ACTIVATE) && \
		$(PYTHON) -m pylint --init-hook="import pylint_venv; pylint_venv.inithook()" src/

run-ruff: venv
	@echo "Running ruff.."
	$(Q)$(PYTHON) -m ruff check src

setup:
	sudo apt-get -y install python3 python3.10-venv

# venv is a shortcut target
venv: $(VENV_NAME)/bin/activate

$(VENV_NAME)/bin/activate: pyproject.toml
	test -d $(VENV_NAME) || python3 -m venv $(VENV_NAME)
	$(PIP) install -e .[tests,dev]
	touch $(@)

distclean: clean
	rm -rf $(VENV_NAME)

clean:
	$(Q)find . -path ./venv -prune -false -o -type d -name __pycache__ -exec rm -rvf {} +
	rm -rf dist
	rm -rf .ruff_cache

.PHONY: all venv run clean distclean run-test setup