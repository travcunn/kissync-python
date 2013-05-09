verify:
	pyflakes -x W smartfile
	pep8 --exclude=migrations --ignore=E501,E225 smartfile

install:
	sudo apt-get install python-sip python-qt4
	python setup.py install
