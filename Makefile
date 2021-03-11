install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	cd tests
	python -m pytest -vv --cov=mylibrary

lint:
	pylint --disable=R,C mylibrary cli scraper tests webapp data_model get_schedule

venv_create: 
	python -m venv ..\.venv

venv_activate:
	.\..\.venv\Scripts\activate

venv: venv_create venv_activate

all: install lint test
