test:
	coverage run tests.py

verify:
	pyflakes .
	pep8 --exclude=migrations --ignore=E501,E225 .

install:
	sudo apt-get install python-pyside
	python setup.py install
