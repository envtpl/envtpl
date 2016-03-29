install:
	python setup.py install

develop:
	python setup.py develop

test:
	flake8 .
	cd tests && nosetests
