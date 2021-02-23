install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	python -m pytest -vv --cov=mylibrary tests/*.py
	## python -m pytest --nbval notebook.ipynb

lint:
	pylint --disable=R,C mylibrary cli scraper tests

setup_windows:
	python -m venv ../.venv

activate_windows:
	../.venv/Scripts/activate

env:
	#Show information about environment
	which python3
	python3 --version
	which pytest
	which pylint

venv_windows: setup_windows activate_windows install

all: install lint test
