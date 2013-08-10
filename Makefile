PYTHON=python

install:
	curl http://peak.telecommunity.com/dist/ez_setup.py | python
	python setup.py install

uninstall:
	yes | pip uninstall PySixel PIL 

clean:
	rm -rf dist/ build/ PySixel.egg-info
	rm -f **/*.pyc

update:
	python setup.py register
	python setup.py sdist upload
	python2.6 setup.py bdist_egg upload
	python2.7 setup.py bdist_egg upload

