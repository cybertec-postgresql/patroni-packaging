VENV_PATH = /tmp/patroni-venv
VENV_ROOT = /tmp/patroni-venv

REV=$(shell git rev-parse --short HEAD)
#DATE=

all: patroni-venv-$(REV).tar.gz

requirements-venv.txt: requirements.txt
	grep -v psycopg2 requirements.txt > requirements-venv.txt

patroni-venv-$(REV).tar.gz: requirements-venv.txt patroni/*.py postgres-telia.yml
	rm -rf $(VENV_PATH)
	virtualenv --distribute $(VENV_PATH)
	. $(VENV_PATH)/bin/activate && pip install -r requirements-venv.txt && pip install --no-deps .
	virtualenv --relocatable $(VENV_PATH)
	find $(VENV_PATH) -name \*py[co] -exec rm {} \;
	find $(VENV_PATH) -name no-global-site-packages.txt -exec rm {} \;
	cp -r extras/ $(VENV_PATH)/
	cp postgres-telia.yml $(VENV_PATH)/extras/postgresql.yml.sample
	tar -C $(VENV_PATH) -cz bin extras include lib lib64 pip-selfcheck.json > patroni-venv-$(REV).tar.gz
	cp patroni-venv-$(REV).tar.gz ../packages/SOURCES/patroni-venv-$(REV).tar.gz

#sed -i "s|`readlink -f $(VENV_ROOT)`||g" $(VENV_PATH)/bin/*
#cp ./conf/pyenv-$(VENV_NAME).spec $(VENV_ROOT)
#tar -C  -cz pyenv-$(VENV_NAME) > $(VENV_ROOT).tgz
#rm -rf $(VENV_ROOT)
