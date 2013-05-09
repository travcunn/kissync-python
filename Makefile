test:
	coverage run tests.py

verify:
	pep8 --exclude=migrations --ignore=E501,E225 .

install:
	sudo apt-get install python-sip python-qt4
	python setup.py install
