install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	python -m pytest -vv --cov=mylibrary tests/*.py
	## python -m pytest --nbval notebook.ipynb

lint:
	pylint --disable=R,C mylibrary cli scraper tests

venv_windows:
	python -m venv ../.venv
	echo "execute ../.venv/Scripts/activate"

env:
	#Show information about environment
	which python3
	python3 --version
	which pytest
	which pylint

all: install lint test
