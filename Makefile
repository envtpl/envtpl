install:
	pip install .

develop:
	pip install -e .

test:
	black --check .
	ruff check .
	cd tests && pytest -vvx

deploy:
	python3 -m build
	twine upload dist/*
