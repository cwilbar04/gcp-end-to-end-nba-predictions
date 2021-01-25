setup:
	python3 -m venv ~/.myrepo

install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	python -m pytest -vv --cov=mylibrary tests/*.py
	## python -m pytest --nbval notebook.ipynb


lint:
	pylint --disable=R,C mylibrary cli

all: install lint test
