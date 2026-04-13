PIP=pip install
DEPENDENCIES= requirements.txt
MAP=test.txt

PYTHON=python3
DEBUGGER= -m pdb

MAIN=main.py

TOCLEAN=.mypy_cache

MYPYFLAGS=--warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

all: install run

install:
	$(PIP) -r $(DEPENDENCIES)

run:
	$(PYTHON) $(MAIN) $(MAP)

debug:
	$(PYTHON) $(DEBUGGER) $(MAIN)

clean:
	py3clean .
	rm -rf $(TOCLEAN)

lint:
	flake8 .
	mypy .  $(MYPYFLAGS)

lint-strict:
	flake8 .
	mypy . --strict