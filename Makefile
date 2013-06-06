test:
	coverage run tests.py

verify:
	pyflakes app
	pep8 --ignore=E501,E225 app

buildui:
	sudo apt-get install pyside-tools
	python builder/buildresources.py ui/images > ui/images/resources.qrc
	pyside-rcc -no-compress ui/images/resources.qrc -o ui/resources.py
	rm ui/images/resources.qrc

install:
	sudo apt-get install python-pyside
	python setup.py install

clean:
	find . -name *.pyc -delete