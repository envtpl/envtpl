install:
	python setup.py install

develop:
	python setup.py develop

test:
	black --check .
	cd tests && pytest -vvx

deploy:
	python3 setup.py sdist bdist_wheel
	twine upload dist/*
