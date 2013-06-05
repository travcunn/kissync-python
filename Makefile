test:
	coverage run tests.py

verify:
	pyflakes app
	pep8 --ignore=E501,E225 app

install:
	sudo apt-get install python-pyside
	python setup.py install

clean:
	find . -name *.pyc -delete