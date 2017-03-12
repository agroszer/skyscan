PYTHON = python2.7

# keep this in sync with versions.cfg!!!
BUILDOUT_VERSION := 2.5.3
SETUPTOOLS_VERSION := 32.3.1

SCRIPTS := bin/main

all: bin/main

venv/bin/python:
	virtualenv -p $(PYTHON) venv
	venv/bin/pip install --upgrade setuptools==$(SETUPTOOLS_VERSION)
	venv/bin/pip install setuptools==$(SETUPTOOLS_VERSION)

bin/buildout: venv/bin/python bootstrap.py
	venv/bin/python bootstrap.py --version=$(BUILDOUT_VERSION)
	touch bin/buildout

$(SCRIPTS): bin/buildout buildout.cfg versions.cfg setup.py
	bin/buildout
	touch -c $(SCRIPTS)

clean:
	git clean -fdx
